// Utility function to safely escape CSS selectors
console.log('✅ [content] Content script loaded on', location.href);

function isGoogleForms() {
  return location.hostname.includes('docs.google.com') && location.pathname.includes('/forms');
}

function isMicrosoftForms() {
  return location.hostname.includes('forms.office.com');
}

// Utility function to safely escape CSS selectors
function cssEscape(value) {
  return CSS.escape(value);
}

// ✅ Native value setter (fix for Google Forms dynamic input detection)
// Utility function to simulate user input in text fields
function fillTextField(input, value) {
  input.focus();
  input.value = value;

  // Trigger React/Angular/Vue-style updates
  input.dispatchEvent(new InputEvent('input', { bubbles: true }));
  input.dispatchEvent(new Event('change', { bubbles: true }));
  input.dispatchEvent(new Event('blur', { bubbles: true }));
}


// Enhanced form scraping for Google Forms with more robust selectors
function scrapeGoogleForm() {
  console.log('🔍 [content] Scraping Google Form...');
  const questions = [];
  
  // Wait for form to be fully loaded
  const formContainer = document.querySelector('form') || document.querySelector('[role="main"]');
  if (!formContainer) {
    console.warn('⚠️ [content] No form container found');
    return questions;
  }
  
  // Find all question containers with multiple selector strategies
  const questionBlocks = document.querySelectorAll([
    'div[role="listitem"]',
    'div[data-params*="entry"]',
    'div.freebirdFormviewerViewItemsItemItem',
    'div[jscontroller][data-value]'
  ].join(', '));
  
  console.log(`🔍 [content] Found ${questionBlocks.length} question blocks`);
  
  questionBlocks.forEach((block, index) => {
    try {
      // Enhanced label detection with multiple strategies
      const labelSelectors = [
        'div[role="heading"]',                     // Headings for questions
        '.freebirdFormviewerViewItemsItemItemTitle', // Classic Forms label
        '.M7eMe',                                   // New Forms label wrapper
        '.Xb9hP',                                   // Another possible label
        'span[jsname]', 
        'span[dir="auto"]'
      ];

      
      let labelElement = null;
      let label = '';
      
      for (const selector of labelSelectors) {
        labelElement = block.querySelector(selector);
        if (labelElement) {
          label = labelElement.textContent?.trim() || labelElement.innerText?.trim() || '';
          if (label && label.length >= 2 && label.length <= 120) break;
        }
      }
      
      if (!label || label.length < 2) {
        label = `Question ${index + 1}`;
        console.log(`⚠️ [content] Using fallback label for block ${index}`);
      }
      
      // Enhanced required field detection
      const isRequired = !!(
        block.querySelector('[aria-required="true"]') || 
        block.querySelector('.freebirdFormviewerViewItemsItemRequiredAsterisk') ||
        block.querySelector('[data-required="true"]') ||
        block.querySelector('.required') ||
        label.includes('*')
      );
      
      // TEXT INPUT - Enhanced detection
      const textSelectors = [
        'input[type="text"]',
        'textarea',
        'input.quantumWizTextinputPaperinputInput',
        'input[jsname][name]',
        'textarea[jsname][name]'
      ];
      
      let textInput = null;
      for (const selector of textSelectors) {
        textInput = block.querySelector(selector);
        if (textInput && textInput.name) break;
      }
      
      if (textInput && textInput.name) {
        questions.push({
          entry: textInput.name,
          type: 'TEXT',
          label: label,
          selector: `[name="${textInput.name}"]`,
          required: isRequired,
          placeholder: textInput.placeholder || ''
        });
        console.log(`✓ [content] Found TEXT field: ${label} (${textInput.name})`);
        return;
      }
      
      // RADIO BUTTONS - Enhanced detection  
      const radioInputs = Array.from(block.querySelectorAll('input[type="radio"][name]'));
      if (radioInputs.length > 0) {
        const firstName = radioInputs[0].name;
        const options = radioInputs.map((radio, radioIndex) => {
          // Multiple strategies to find option labels
          const optionLabelSelectors = [
            'label',
            '[data-text]',
            'span[dir="auto"]',
            '.aDTYNe',
            '.AB7Lab'
          ];
          
          let optionLabel = null;
          let optionText = '';
          
          // Look in parent elements
          let parent = radio.parentElement;
          for (let i = 0; i < 3 && parent; i++) {
            for (const selector of optionLabelSelectors) {
              optionLabel = parent.querySelector(selector);
              if (optionLabel) {
                optionText = optionLabel.textContent?.trim() || '';
                if (optionText) break;
              }
            }
            if (optionText) break;
            parent = parent.parentElement;
          }
          
          return {
            value: radio.value || `option_${radioIndex}`,
            text: optionText || radio.value || `Option ${radioIndex + 1}`,
            selector: `input[name="${firstName}"][value="${cssEscape(radio.value || `option_${radioIndex}`)}"]`
          };
        });
        
        questions.push({
          entry: firstName,
          type: 'RADIO',
          label: label,
          options: options,
          required: isRequired
        });
        console.log(`✓ [content] Found RADIO field: ${label} (${firstName}) with ${options.length} options`);
        return;
      }
      
      // CHECKBOXES - Enhanced detection
      const checkboxInputs = Array.from(block.querySelectorAll('input[type="checkbox"][name]'));
      if (checkboxInputs.length > 0) {
        const firstName = checkboxInputs[0].name;
        const options = checkboxInputs.map((checkbox, checkboxIndex) => {
          // Similar label detection as radio buttons
          let optionText = '';
          let parent = checkbox.parentElement;
          
          for (let i = 0; i < 3 && parent; i++) {
            const labels = parent.querySelectorAll('[data-text], span[dir="auto"], .aDTYNe');
            for (const label of labels) {
              const text = label.textContent?.trim();
              if (text && text.length > 0) {
                optionText = text;
                break;
              }
            }
            if (optionText) break;
            parent = parent.parentElement;
          }
          
          return {
            value: checkbox.value || `option_${checkboxIndex}`,
            text: optionText || checkbox.value || `Option ${checkboxIndex + 1}`,
            selector: `input[name="${firstName}"][value="${cssEscape(checkbox.value || `option_${checkboxIndex}`)}"]`
          };
        });
        
        questions.push({
          entry: firstName,
          type: 'CHECKBOX',
          label: label,
          options: options,
          required: isRequired
        });
        console.log(`✓ [content] Found CHECKBOX field: ${label} (${firstName}) with ${options.length} options`);
        return;
      }
      
      // DROPDOWN/SELECT - Enhanced detection
      const selectElement = block.querySelector('select[name]') || 
                           block.querySelector('div[role="listbox"]') ||
                           block.querySelector('.quantumWizMenuPaperselectEl');
      
      if (selectElement && selectElement.name) {
        const options = Array.from(selectElement.options || [])
          .filter(option => option.value && option.value !== '')
          .map(option => ({
            value: option.value,
            text: option.textContent?.trim() || option.value
          }));
        
        if (options.length > 0) {
          questions.push({
            entry: selectElement.name,
            type: 'DROPDOWN',
            label: label,
            options: options,
            selector: `select[name="${selectElement.name}"]`,
            required: isRequired
          });
          console.log(`✓ [content] Found DROPDOWN field: ${label} (${selectElement.name}) with ${options.length} options`);
        }
        return;
      }
      
    } catch (error) {
      console.error(`❌ [content] Error processing question block ${index}:`, error);
    }
  });
  
  console.log(`✅ [content] Scraped form schema: ${questions.length} fields total`);
  return questions;
}

// Microsoft Forms scraping
function scrapeMicrosoftForm() {
  console.log('🔍 [content] Scraping Microsoft Form...');
  const questions = [];

  const form = document.querySelector('form') || document.body;
  if (!form) return questions;

  const blocks = form.querySelectorAll('[role="group"], div[aria-labelledby], div[class*="question"], div[data-automation-id*="question"]');
  console.log(`🔍 [content] Found ${blocks.length} MS question blocks`);

  blocks.forEach((block, index) => {
    try {
      // Label
      let label = '';
      const ariaLabelledBy = block.getAttribute('aria-labelledby');
      if (ariaLabelledBy) {
        const lbl = document.getElementById(ariaLabelledBy);
        if (lbl) label = (lbl.textContent || '').trim();
      }
      if (!label) {
        const lblEl = block.querySelector('label, [role="heading"], .question-title, h1, h2, h3, [data-automation-id*="questionTitle"]');
        if (lblEl) label = (lblEl.textContent || '').trim();
      }
      if (!label) label = `Question ${index + 1}`;

      const isRequired = !!(block.querySelector('[aria-required="true"], .required, [data-required="true"]'));

      // Text input
      const textInput = block.querySelector('input[type="text"][name], textarea[name]');
      if (textInput && textInput.name) {
        questions.push({
          entry: textInput.name,
          type: 'TEXT',
          label,
          selector: `[name="${textInput.name}"]`,
          required: isRequired,
          placeholder: textInput.placeholder || ''
        });
        return;
      }

      // Radios
      const radios = Array.from(block.querySelectorAll('input[type="radio"][name]'));
      if (radios.length) {
        const firstName = radios[0].name;
        const options = radios.map((el, i) => {
          let optionText = '';
          const lbl = el.closest('label');
          if (lbl) optionText = (lbl.textContent || '').trim();
          return {
            value: el.value || `option_${i}`,
            text: optionText || el.value || `Option ${i + 1}`,
            selector: `input[type="radio"][name="${firstName}"][value="${CSS.escape(el.value || `option_${i}`)}"]`
          };
        });
        questions.push({ entry: firstName, type: 'RADIO', label, options, required: isRequired });
        return;
      }

      // Checkboxes
      const checks = Array.from(block.querySelectorAll('input[type="checkbox"][name]'));
      if (checks.length) {
        const firstName = checks[0].name;
        const options = checks.map((el, i) => {
          let optionText = '';
          const lbl = el.closest('label');
          if (lbl) optionText = (lbl.textContent || '').trim();
          return {
            value: el.value || `option_${i}`,
            text: optionText || el.value || `Option ${i + 1}`,
            selector: `input[type="checkbox"][name="${firstName}"][value="${CSS.escape(el.value || `option_${i}`)}"]`
          };
        });
        questions.push({ entry: firstName, type: 'CHECKBOX', label, options, required: isRequired });
        return;
      }

      // Dropdown (native)
      const select = block.querySelector('select[name]');
      if (select && select.name) {
        const options = Array.from(select.options || [])
          .filter(o => o.value && o.value !== '')
          .map(o => ({ value: o.value, text: (o.textContent || '').trim() }));
        if (options.length) {
          questions.push({ entry: select.name, type: 'DROPDOWN', label, options, selector: `select[name="${select.name}"]`, required: isRequired });
          return;
        }
      }
    } catch (e) {
      console.warn('⚠️ [content] MS block error', e);
    }
  });

  console.log(`✅ [content] Scraped MS form schema: ${questions.length} fields total`);
  return questions;
}

function scrapeFormAuto() {
  if (isGoogleForms()) return scrapeGoogleForm();
  if (isMicrosoftForms()) return scrapeMicrosoftForm();
  return [];
}

// Initialize form scraping when page loads
function initializeFormScraping() {
  console.log('🔄 [content] Initializing form scraping...');
  
  // Multiple attempts with different delays for dynamic loading
  const attempts = [1000, 3000, 5000]; // Try after 1s, 3s, and 5s
  
  attempts.forEach((delay, index) => {
    setTimeout(() => {
      const schema = scrapeFormAuto();
      if (schema.length > 0) {
        // Send schema to background script
        chrome.runtime.sendMessage({
          type: 'SCHEMA_UPDATE',
          schema: schema
        }).catch(error => {
          console.error('❌ [content] Failed to send schema to background:', error);
        });
        
        console.log(`📤 [content] Sent schema with ${schema.length} questions to background script (attempt ${index + 1})`);
        
        // Stop further attempts if we got a good schema
        if (schema.length > 3) return;
      } else {
        console.log(`⚠️ [content] No form questions found on attempt ${index + 1}`);
      }
    }, delay);
  });
}

// Enhanced form filling with better error handling
function fillFormWithAnswers(answers) {
  console.log('🎯 [content] Filling form with answers:', answers);
  
  if (!answers || Object.keys(answers).length === 0) {
    console.warn('⚠️ [content] No answers provided');
    showNotification('No answers provided by AI', 'error');
    return;
  }
  
  // Get the current schema
  const currentSchema = scrapeFormAuto();
  let filledCount = 0;
  let errorCount = 0;
  
  currentSchema.forEach(field => {
    const answer = answers[field.entry];
    if (answer === undefined || answer === null) {
      console.log(`⏭️ [content] Skipping field: ${field.label} (${field.entry}) - no answer`);
      return;
    }
    
    console.log(`🔧 [content] Filling field "${field.label}" with:`, answer);
    
    try {
      switch (field.type) {
        case 'TEXT':
          const textElement = document.querySelector(field.selector);
          if (textElement) {
            fillTextField(textElement, String(answer));
            console.log(`✅ [content] Filled text field: ${field.label}`);
            filledCount++;
          } else {
            console.warn(`❌ [content] Text element not found: ${field.selector}`);
            errorCount++;
          }
          break;

        case 'RADIO':
          let radioFilled = false;
          field.options.forEach(option => {
            if (option.value === answer || option.text === answer || 
                option.text.toLowerCase().includes(answer.toString().toLowerCase())) {
              const radioElement = document.querySelector(option.selector);
              if (radioElement) {
                radioElement.focus();
                radioElement.click();
                radioFilled = true;
                console.log(`✅ [content] Selected radio option: ${option.text}`);
                filledCount++;
              }
            }
          });
          if (!radioFilled) {
            console.warn(`❌ [content] No matching radio option found for: ${answer}`);
            errorCount++;
          }
          break;
          
        case 'CHECKBOX':
          const checkboxAnswers = Array.isArray(answer) ? answer : [answer];
          let checkboxFilled = false;
          
          checkboxAnswers.forEach(ans => {
            field.options.forEach(option => {
              if (option.value === ans || option.text === ans ||
                  option.text.toLowerCase().includes(ans.toString().toLowerCase())) {
                const checkboxElement = document.querySelector(option.selector);
                if (checkboxElement && !checkboxElement.checked) {
                  checkboxElement.focus();
                  checkboxElement.click();
                  console.log(`✅ [content] Checked checkbox option: ${option.text}`);
                  checkboxFilled = true;
                }
              }
            });
          });
          
          if (checkboxFilled) filledCount++;
          else {
            console.warn(`❌ [content] No matching checkbox options found for:`, checkboxAnswers);
            errorCount++;
          }
          break;
          
        case 'DROPDOWN':
          const selectElement = document.querySelector(field.selector);
          if (selectElement) {
            let optionSelected = false;
            
            // Try exact matches first, then partial matches
            for (let option of selectElement.options) {
              if (option.value === answer || option.textContent.trim() === answer) {
                selectElement.value = option.value;
                selectElement.focus();
                selectElement.dispatchEvent(new Event('change', { bubbles: true }));
                optionSelected = true;
                console.log(`✅ [content] Selected dropdown option: ${option.textContent.trim()}`);
                filledCount++;
                break;
              }
            }
            
            // If no exact match, try partial match
            if (!optionSelected) {
              for (let option of selectElement.options) {
                if (option.textContent.toLowerCase().includes(answer.toString().toLowerCase())) {
                  selectElement.value = option.value;
                  selectElement.focus();
                  selectElement.dispatchEvent(new Event('change', { bubbles: true }));
                  optionSelected = true;
                  console.log(`✅ [content] Selected dropdown option (partial): ${option.textContent.trim()}`);
                  filledCount++;
                  break;
                }
              }
            }

            // Microsoft Forms styled listbox
            if (!optionSelected) {
              const listbox = document.querySelector('div[role="listbox"]');
              if (listbox) {
                const options = listbox.querySelectorAll('[role="option"]');
                for (const opt of options) {
                  const text = (opt.textContent || '').trim();
                  if (text === answer || text.toLowerCase().includes(String(answer).toLowerCase())) {
                    opt.click();
                    optionSelected = true;
                    filledCount++;
                    console.log(`✅ [content] Selected listbox option: ${text}`);
                    break;
                  }
                }
              }
            }
            
            if (!optionSelected) {
              console.warn(`❌ [content] No matching dropdown option found for: ${answer}`);
              errorCount++;
            }
          } else {
            console.warn(`❌ [content] Select element not found: ${field.selector}`);
            errorCount++;
          }
          break;
          
        default:
          console.warn(`❓ [content] Unknown field type: ${field.type}`);
          errorCount++;
      }
    } catch (error) {
      console.error(`❌ [content] Error filling field ${field.label}:`, error);
      errorCount++;
    }
  });
  
  // Show summary notification
  const totalFields = Object.keys(answers).length;
  if (filledCount > 0) {
    showNotification(`✅ Filled ${filledCount}/${totalFields} fields successfully!`, 'success');
  } else if (errorCount > 0) {
    showNotification(`❌ Failed to fill any fields. Check form compatibility.`, 'error');
  }
  
  console.log(`📊 [content] Form filling summary: ${filledCount} filled, ${errorCount} errors`);
}

// Enhanced notification system
function showNotification(message, type = 'success') {
  // Remove existing notifications
  const existing = document.querySelector('.smart-filler-notification');
  if (existing) existing.remove();
  
  const notification = document.createElement('div');
  notification.className = 'smart-filler-notification';
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 16px 20px;
    background: ${type === 'success' ? '#4CAF50' : type === 'error' ? '#f44336' : '#ff9800'};
    color: white;
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    z-index: 10000;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    font-size: 14px;
    font-weight: 500;
    max-width: 350px;
    line-height: 1.4;
    animation: slideIn 0.3s ease-out;
  `;
  
  // Add slide-in animation
  const style = document.createElement('style');
  style.textContent = `
    @keyframes slideIn {
      from { transform: translateX(100%); opacity: 0; }
      to { transform: translateX(0); opacity: 1; }
    }
  `;
  document.head.appendChild(style);
  
  notification.textContent = message;
  document.body.appendChild(notification);
  
  setTimeout(() => notification.remove(), 6000);
}

// Enhanced message listener
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('📨 [content] Received message:', message.type);
  
  try {
    switch (message.type) {
      case 'GET_SCHEMA':
        const schema = scrapeFormAuto();
        chrome.runtime.sendMessage({
          type: 'SCHEMA_UPDATE',
          schema: schema
        }).catch(error => {
          console.error('❌ [content] Failed to send schema update:', error);
        });
        sendResponse({ success: true, schemaLength: schema.length });
        break;
        
      case 'FILL_ANSWERS':
        fillFormWithAnswers(message.answers);
        sendResponse({ success: true });
        break;
        
      case 'FILL_ERROR':
        console.error('❌ [content] Form filling error:', message.error);
        showNotification(`❌ Error: ${message.error}`, 'error');
        sendResponse({ success: true });
        break;
        
      default:
        console.warn('❓ [content] Unknown message type:', message.type);
    }
  } catch (error) {
    console.error('❌ [content] Error handling message:', error);
    sendResponse({ success: false, error: error.message });
  }
  
  return true; // Keep message channel open
});

// Initialize when page loads
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeFormScraping);
} else {
  initializeFormScraping();
}

// Enhanced form change observer
const observer = new MutationObserver((mutations) => {
  let shouldRescrape = false;
  
  mutations.forEach(mutation => {
    if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
      // Check if new form elements were added
      for (const node of mutation.addedNodes) {
        if (node.nodeType === Node.ELEMENT_NODE) {
          if (node.matches && (
            node.matches('div[role="listitem"]') ||
            node.matches('input[name]') ||
            node.matches('select[name]') ||
            node.querySelector && node.querySelector('input[name], select[name]')
          )) {
            shouldRescrape = true;
            break;
          }
        }
      }
    }
  });
  
  if (shouldRescrape) {
    console.log('🔄 [content] Form structure changed, re-scraping...');
    setTimeout(initializeFormScraping, 2000);
  }
});

observer.observe(document.body, {
  childList: true,
  subtree: true
});

console.log('🚀 [content] Smart Form Filler content script fully loaded');

// 1. **Enhanced form scraping** - Multiple selector strategies for different Google Forms versions
// 2. **Better label detection** - Multiple fallback methods to find field labels  
// 3. **Improved option detection** - Better detection of radio/checkbox option labels
// 4. **Multiple scraping attempts** - Try scraping at different intervals for dynamic loading
// 5. **Enhanced form filling** - Better event triggering and partial text matching
// 6. **Error tracking** - Count successful vs failed field fills
// 7. **Better notifications** - More detailed user feedback with animations
// 8. **Robust message handling** - Better error handling in message listeners
// 9. **Smart form change detection** - Only re-scrape when actual form elements change
// 10. **Enhanced logging** - More detailed console output for debugging
