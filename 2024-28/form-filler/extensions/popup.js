
document.addEventListener('DOMContentLoaded', async () => {

    // Load saved settings
  const settings = await chrome.storage.sync.get([
    'geminiKey', 'groqKey', 'pineconeKey', 'pineconeEnv', 'pineconeHost'
  ]);
  
  if (settings.geminiKey) document.getElementById('geminiKey').value = settings.geminiKey;
  if (settings.groqKey) document.getElementById('groqKey').value = settings.groqKey;
  if (settings.pineconeKey) document.getElementById('pineconeKey').value = settings.pineconeKey;
  if (settings.pineconeEnv) document.getElementById('pineconeEnv').value = settings.pineconeEnv;
  if (settings.pineconeHost) document.getElementById('pineconeHost').value = settings.pineconeHost;
  
  console.log('🔄 [popup] Loaded settings:', {
    gemini: !!settings.geminiKey,
    groq: !!settings.groqKey,
    pinecone: !!settings.pineconeKey,
    env: !!settings.pineconeEnv
  });
});

function showStatus(message, type = 'success') {
  const status = document.getElementById('status');
  status.textContent = message;
  status.className = `status ${type}`;
  status.style.display = 'block';
  
  // Auto-hide after longer delay
  setTimeout(() => {
    status.style.display = 'none';
  }, type === 'error' ? 8000 : 5000);
}

// Handle PDF file selection
document.getElementById('pdfFile').addEventListener('change', (e) => {
  const files = e.target.files;
  const pdfInfo = document.getElementById('pdfInfo');
  
  if (files.length > 0) {
    pdfInfo.style.display = 'block';
    pdfInfo.innerHTML = `
      <strong>Selected PDFs:</strong><br>
      ${Array.from(files).map(f => `• ${f.name} (${(f.size/1024/1024).toFixed(1)} MB)`).join('<br>')}
    `;
  } else {
    pdfInfo.style.display = 'none';
  }
});

// Upload and process PDFs
document.getElementById('uploadPdfs').addEventListener('click', async () => {
  const files = document.getElementById('pdfFile').files;
  const settings = await chrome.storage.sync.get(['geminiKey', 'pineconeKey', 'pineconeEnv', 'pineconeHost']);
  if (files.length === 0) {
    showStatus('Please select PDF files first', 'error');
    return;
  }
  
  const hasEnvOrHost = !!settings.pineconeEnv || !!settings.pineconeHost;
  if (!settings.geminiKey || !settings.pineconeKey || !hasEnvOrHost) {
    showStatus('Please save API keys and Pinecone env or host first', 'error');
    return;
  }
  
  const uploadBtn = document.getElementById('uploadPdfs');
  const originalText = uploadBtn.textContent;
  uploadBtn.textContent = '⏳ Processing...';
  uploadBtn.disabled = true;
  
  try {
    showStatus('Uploading PDFs to server...', 'info');
    
    const formData = new FormData();
    for (let file of files) {
      formData.append('pdfs', file);
    }
    formData.append('gemini_key', settings.geminiKey);
    formData.append('pinecone_key', settings.pineconeKey);
    formData.append('pinecone_env', settings.pineconeEnv);
    if (settings.pineconeHost) formData.append('pinecone_host', settings.pineconeHost);
    
    // Test backend connection first
    try {
      const healthCheck = await fetch('http://localhost:8000/', { method: 'GET' });
      if (!healthCheck.ok) {
        throw new Error('Backend health check failed');
      }
    } catch (healthError) {
      throw new Error('Backend server not responding. Make sure it\'s running on localhost:8000');
    }
    
    const response = await fetch('http://localhost:8000/upload-pdfs', {
      method: 'POST',
      body: formData
    });
    
    if (response.ok) {
      const result = await response.json();
      showStatus(`Successfully processed ${result.chunks_count} document chunks`, 'success');
      document.getElementById('pdfFile').value = ''; // Clear file input
      document.getElementById('pdfInfo').style.display = 'none';
      console.log('✅ [popup] PDF upload successful:', result);
    } else {
      const errorText = await response.text();
      throw new Error(`Server error: ${response.status} - ${errorText}`);
    }
    
  } catch (error) {
    console.error('❌ [popup] Upload error:', error);
    showStatus(`Failed to upload PDFs: ${error.message}`, 'error');
  } finally {
    uploadBtn.textContent = originalText;
    uploadBtn.disabled = false;
  }
});

// Save settings
document.getElementById('saveSettings').addEventListener('click', async () => {
  const settings = {
    geminiKey: document.getElementById('geminiKey').value.trim(),
    groqKey: document.getElementById('groqKey').value.trim(),
    pineconeKey: document.getElementById('pineconeKey').value.trim(),
    pineconeEnv: document.getElementById('pineconeEnv').value.trim(),
    pineconeHost: document.getElementById('pineconeHost').value.trim()
  };
  
  const hasEnvOrHostSave = !!settings.pineconeEnv || !!settings.pineconeHost;
  if (!settings.geminiKey || !settings.groqKey || !settings.pineconeKey || !hasEnvOrHostSave) {
    showStatus('Please provide Gemini, Groq, Pinecone Key, and Pinecone Env or Host', 'error');
    return;
  }
  
  try {
    await chrome.storage.sync.set(settings);
    showStatus('Settings saved successfully!', 'success');
    console.log('✅ [popup] Settings saved');
    
    // Test backend connection
    try {
      const response = await fetch('http://localhost:8000/', { method: 'GET' });
      if (response.ok) {
        console.log('✅ [popup] Backend connection verified');
      } else {
        console.warn('⚠️ [popup] Backend responded with error:', response.status);
        showStatus('Settings saved, but backend connection failed. Make sure server is running.', 'warning');
      }
    } catch (error) {
      console.warn('⚠️ [popup] Backend connection test failed:', error.message);
      showStatus('Settings saved, but backend connection failed. Make sure server is running.', 'warning');
    }
    
  } catch (error) {
    console.error('❌ [popup] Failed to save settings:', error);
    showStatus('Failed to save settings', 'error');
  }
});

// Fill current form - MAIN FIX HERE
document.getElementById('fillForm').addEventListener('click', async () => {
  console.log('🔘 [popup] Fill button clicked');
  
  const fillBtn = document.getElementById('fillForm');
  const originalText = fillBtn.textContent;
  
  try {
    // Get active tab
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    console.log('🔎 [popup] Active tab URL:', tab.url);
    
    const isGoogle = tab.url.includes('docs.google.com/forms');
    const isMicrosoft = tab.url.includes('forms.office.com');
    if (!isGoogle && !isMicrosoft) {
      throw new Error('Please navigate to a Google or Microsoft Form first');
    }
    
    // Get settings
    const settings = await chrome.storage.sync.get([
      'geminiKey', 'groqKey', 'pineconeKey', 'pineconeEnv', 'pineconeHost'
    ]);
    
    console.log('🔑 [popup] Settings check:', {
      gemini: !!settings.geminiKey,
      groq: !!settings.groqKey, 
      pinecone: !!settings.pineconeKey,
      env: !!settings.pineconeEnv
    });
    
    const hasEnvOrHostFill = !!settings.pineconeEnv || !!settings.pineconeHost;
    if (!settings.geminiKey || !settings.groqKey || !settings.pineconeKey || !hasEnvOrHostFill) {
      throw new Error('Please save API keys and Pinecone env or host first');
    }
    
    // Update UI
    fillBtn.disabled = true;
    fillBtn.textContent = '🤖 Filling…';
    showStatus('Initiating form fill process...', 'info');
    
    // Send message to background script with proper response handling
    console.log('📤 [popup] Sending FILL_FORM message to background...');
    
    const response = await new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        reject(new Error('Timeout waiting for response from background script (30s)'));
      }, 30000); // 30 second timeout
      
      chrome.runtime.sendMessage({
        type: 'FILL_FORM',
        settings: settings,
        tabId: tab.id
      }, (response) => {
        clearTimeout(timeout);
        
        if (chrome.runtime.lastError) {
          console.error('❌ [popup] Runtime error:', chrome.runtime.lastError.message);
          reject(new Error(`Extension error: ${chrome.runtime.lastError.message}`));
        } else {
          console.log('📥 [popup] Received response from background:', response);
          resolve(response);
        }
      });
    });
    
    // Handle response
    if (response && response.success) {
      const message = response.answersCount ? 
        `Form filled successfully with ${response.answersCount} answers!` :
        'Form filled successfully!';
      showStatus(message, 'success');
      console.log('✅ [popup] Form fill completed successfully');
    } else {
      throw new Error(response?.error || 'Unknown error occurred during form filling');
    }
    
  } catch (error) {
    console.error('❌ [popup] Form fill failed:', error);
    showStatus(`Form fill failed: ${error.message}`, 'error');
  } finally {
    fillBtn.disabled = false;
    fillBtn.textContent = originalText;
  }
});

// Add keyboard shortcuts
document.addEventListener('keydown', (e) => {
  if (e.ctrlKey || e.metaKey) {
    switch (e.key) {
      case 's':
        e.preventDefault();
        document.getElementById('saveSettings').click();
        break;
      case 'Enter':
        e.preventDefault();
        document.getElementById('fillForm').click();
        break;
    }
  }
});

// Add version info and debug helpers
console.log('🚀 [popup] Smart Form Filler popup loaded');
console.log('🔧 [popup] Debug commands available:');
console.log('  - chrome.storage.sync.get() to check stored settings');
console.log('  - chrome.tabs.query({active:true,currentWindow:true}) to check active tab');

// Add status info helper  
window.showDebugInfo = async () => {
  const settings = await chrome.storage.sync.get();
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  console.log('🔍 [popup] Debug Info:', {
    settings: settings,
    currentTab: tab.url,
    isGoogleForm: tab.url.includes('docs.google.com/forms')
  });
};
{/* /* ## Key Fixes in popup.js:

1. **Proper async response handling** - Now properly waits for and handles responses from background script
2. **Better error propagation** - Errors from background script are properly caught and displayed
3. **Enhanced validation** - Check all required fields before proceeding
4. **Backend connectivity testing** - Test backend connection before operations
5. **Improved UI feedback** - Better loading states and error messages
6. **Promise-based message handling** - Proper timeout and error handling for message passing
7. **Debug helpers** - Added console commands for troubleshooting
8. **Keyboard shortcuts** - Added Ctrl+S for save and Ctrl+Enter for fill
9. **Enhanced logging** - More detailed console output for debugging
10. **Timeout handling** - 30-second timeout for form filling operations */ }