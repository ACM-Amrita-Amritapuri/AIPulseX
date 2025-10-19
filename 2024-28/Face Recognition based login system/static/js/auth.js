(() => {
'use strict';

const body = document.body;
const currentPage = body ? body.dataset.page || 'home' : 'home';

const modalLayer = document.querySelector('[data-modal-layer]');
const modalTitle = document.getElementById('modalTitle');
const modalMessage = document.getElementById('modalMessage');
const modalPrimary = document.getElementById('modalPrimaryAction');

const apiRoutes = {
    register: '/register',
    loginFace: '/login_face',
    loginCred: '/login_cred'
};

function toggleModal({ title, message, variant = 'info', primaryText, onPrimary } = {}) {
    if (!modalLayer || !modalTitle || !modalMessage || !modalPrimary) {
        return;
    }

    const open = Boolean(title && message);

    if (!open) {
        modalLayer.hidden = true;
        modalLayer.removeAttribute('data-variant');
        modalPrimary.hidden = true;
        modalPrimary.onclick = null;
        return;
    }

    modalLayer.dataset.variant = variant;
    modalTitle.textContent = title;
    modalMessage.textContent = message;

    if (primaryText && typeof onPrimary === 'function') {
        modalPrimary.hidden = false;
        modalPrimary.textContent = primaryText;
        modalPrimary.onclick = () => {
            toggleModal();
            onPrimary();
        };
    } else {
        modalPrimary.hidden = true;
        modalPrimary.onclick = null;
    }

    modalLayer.hidden = false;
}

function setChip(element, text, tone) {
    if (!element) {
        return;
    }
    element.textContent = text;
    if (tone) {
        element.dataset.tone = tone;
    } else {
        delete element.dataset.tone;
    }
}

function setInstruction(element, text) {
    if (element) {
        element.textContent = text;
    }
}

const streamManager = (() => {
    let stream = null;
    const attached = new Set();

    async function start(video, customConstraints) {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            throw new Error('Camera access is not supported by this browser.');
        }

        const constraints = {
            video: Object.assign({
                width: { ideal: 960 },
                height: { ideal: 540 },
                facingMode: 'user'
            }, customConstraints || {}),
            audio: false
        };

        if (!stream) {
            stream = await navigator.mediaDevices.getUserMedia(constraints);
        }

        if (video) {
            attach(video);
        }

        return stream;
    }

    function attach(video) {
        if (!stream || !video) {
            return;
        }
        video.srcObject = stream;
        video.play().catch(() => undefined);
        attached.add(video);
    }

    function stop() {
        attached.forEach((video) => {
            video.pause();
            video.srcObject = null;
        });
        attached.clear();
        if (stream) {
            stream.getTracks().forEach((track) => track.stop());
        }
        stream = null;
    }

    function capture(video, canvas) {
        if (!stream || !video || !canvas) {
            throw new Error('Camera stream not ready.');
        }
        if (video.readyState < 2) {
            throw new Error('Video feed not ready yet.');
        }
        const width = video.videoWidth || 640;
        const height = video.videoHeight || 480;
        canvas.width = width;
        canvas.height = height;
        const context = canvas.getContext('2d');
        if (!context) {
            throw new Error('Unable to access drawing context.');
        }
        context.drawImage(video, 0, 0, width, height);
        const dataUrl = canvas.toDataURL('image/jpeg', 0.92);
        const separator = dataUrl.indexOf(',');
        if (separator === -1) {
            throw new Error('Failed to capture frame.');
        }
        return dataUrl.slice(separator + 1);
    }

    function isActive() {
        return Boolean(stream);
    }

    return { start, stop, capture, attach, isActive };
})();

async function submitJSON(url, payload) {
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    });

    let data;
    try {
        data = await response.json();
    } catch (error) {
        data = { message: 'Unexpected server response.' };
    }

    return { ok: response.ok, status: response.status, data };
}

function setupNavigation() {
    const navToggle = document.querySelector('.nav-toggle');
    const navLinks = document.querySelector('.nav-links');
    const navAnchors = navLinks ? navLinks.querySelectorAll('.nav-link') : [];

    navAnchors.forEach((anchor) => {
        const route = anchor.dataset.route;
        if (route === currentPage) {
            anchor.classList.add('active');
        } else {
            anchor.classList.remove('active');
        }

        anchor.addEventListener('click', () => {
            if (!navToggle || !navLinks) {
                return;
            }
            navToggle.setAttribute('aria-expanded', 'false');
            navLinks.classList.remove('is-open');
        });
    });

    if (navToggle && navLinks) {
        navToggle.addEventListener('click', () => {
            const expanded = navToggle.getAttribute('aria-expanded') === 'true';
            const nextExpanded = !expanded;
            navToggle.setAttribute('aria-expanded', String(nextExpanded));
            navLinks.classList.toggle('is-open', nextExpanded);
        });
    }
}

function registerModalHandlers() {
    if (!modalLayer) {
        return;
    }
    modalLayer.addEventListener('click', (event) => {
        if (event.target === modalLayer) {
            toggleModal();
        }
    });
    modalLayer.querySelectorAll('[data-modal-close]').forEach((button) => {
        button.addEventListener('click', () => toggleModal());
    });
}

function setupRevealAnimations() {
    const animatedBlocks = document.querySelectorAll('[data-animate]');
    if (!animatedBlocks.length) {
        return;
    }

    if (!('IntersectionObserver' in window)) {
        animatedBlocks.forEach((element) => {
            element.dataset.visible = 'true';
        });
        return;
    }

    const observer = new IntersectionObserver((entries, obs) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.dataset.visible = 'true';
                obs.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.2,
        rootMargin: '0px 0px -40px 0px'
    });

    animatedBlocks.forEach((element) => observer.observe(element));
}

function initRegisterPage() {
    const form = document.getElementById('registerForm');
    const enableButton = document.getElementById('registerEnableFace');
    const captureButton = document.getElementById('registerCapture');
    const enableStatus = document.getElementById('registerEnableStatus');
    const captureStatus = document.getElementById('registerCaptureStatus');
    const videoWrapper = document.querySelector('[data-face-wrapper]');
    const video = document.getElementById('registerVideo');
    const canvas = document.getElementById('registerCanvas');
    const instruction = document.getElementById('registerInstruction');
    const cameraBadge = document.getElementById('registerStatus');

    if (!form || !enableButton || !captureButton || !video || !canvas) {
        return;
    }

    let faceEnabled = false;
    let snapshot = null;

    setChip(enableStatus, 'Face capture inactive');
    setChip(captureStatus, 'No capture yet');

    function resetCameraState() {
        snapshot = null;
        captureButton.disabled = true;
        streamManager.stop();
        if (videoWrapper) {
            videoWrapper.hidden = true;
        }
        setChip(captureStatus, 'No capture yet');
        setChip(cameraBadge, 'Camera idle');
        setInstruction(instruction, 'Camera inactive until you enable enrollment.');
    }

    enableButton.addEventListener('click', async () => {
        if (!faceEnabled) {
            try {
                await streamManager.start(video);
                if (videoWrapper) {
                    videoWrapper.hidden = false;
                }
                captureButton.disabled = false;
                faceEnabled = true;
                enableButton.textContent = 'Disable face authentication';
                setChip(enableStatus, 'Face capture enabled', 'success');
                setChip(cameraBadge, 'Camera ready', 'success');
                setInstruction(instruction, 'Align your face within the frame before capturing.');
            } catch (error) {
                const message = error instanceof Error ? error.message : 'Unable to access camera.';
                setChip(enableStatus, 'Camera blocked', 'error');
                setInstruction(instruction, 'Grant camera permissions to enable face authentication.');
                toggleModal({
                    title: 'Camera permission required',
                    message,
                    variant: 'warning'
                });
            }
        } else {
            faceEnabled = false;
            enableButton.textContent = 'Enable face authentication';
            setChip(enableStatus, 'Face capture inactive');
            resetCameraState();
        }
    });

    captureButton.addEventListener('click', () => {
        if (!faceEnabled) {
            toggleModal({
                title: 'Enable face authentication first',
                message: 'Turn on face authentication before capturing a snapshot.',
                variant: 'warning'
            });
            return;
        }

        try {
            snapshot = streamManager.capture(video, canvas);
            setChip(captureStatus, 'Snapshot captured', 'success');
            setInstruction(instruction, 'Snapshot locked in. Submit the form when ready.'); // Let users know capture finished
            setChip(cameraBadge, 'Capture complete', 'success');
            toggleModal({
                title: 'Snapshot ready',
                message: 'Face snapshot captured successfully. Complete enrollment to finish.',
                variant: 'success'
            });
        } catch (error) {
            const message = error instanceof Error ? error.message : 'Capture failed. Adjust lighting and retry.';
            setChip(captureStatus, 'Capture failed', 'error');
            setInstruction(instruction, 'Capture interrupted. Reposition and try again.');
            toggleModal({
                title: 'Capture failed',
                message,
                variant: 'warning'
            });
        }
    });

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        const usernameInput = document.getElementById('registerUsername');
        const passwordInput = document.getElementById('registerPassword');
        const confirmInput = document.getElementById('registerConfirm');

        const username = usernameInput ? usernameInput.value.trim() : '';
        const password = passwordInput ? passwordInput.value : '';
        const confirmPassword = confirmInput ? confirmInput.value : '';

        const issues = [];
        if (!username) {
            issues.push('Username is required.');
        }
        if (!password) {
            issues.push('Password is required.');
        }
        if (password !== confirmPassword) {
            issues.push('Passwords do not match.');
        }
        if (!faceEnabled) {
            issues.push('Enable face authentication to capture your embedding.');
        }
        if (!snapshot) {
            issues.push('Capture a face snapshot before submitting.');
        }

        if (issues.length) {
            toggleModal({
                title: 'Check your details',
                message: issues.join(' '),
                variant: 'warning'
            });
            return;
        }

        const submitButton = form.querySelector("button[type='submit']");
        if (!submitButton) {
            return;
        }

        submitButton.disabled = true;
        submitButton.textContent = 'Submitting...';

        try {
            const payload = {
                username,
                password,
                confirm_password: confirmPassword,
                face_image: snapshot
            };
            const { ok, data } = await submitJSON(apiRoutes.register, payload);
            if (ok) {
                toggleModal({
                    title: 'Enrollment complete',
                    message: data.message || 'Registration successful. You can now log in with your face.',
                    variant: 'success'
                });
                form.reset();
                faceEnabled = false;
                enableButton.textContent = 'Enable face authentication';
                setChip(enableStatus, 'Face capture inactive');
                resetCameraState();
            } else {
                const message = data?.message || data?.messages?.join(' ') || 'Registration failed.';
                toggleModal({
                    title: 'Registration error',
                    message,
                    variant: 'error'
                });
            }
        } catch (error) {
            const message = error instanceof Error ? error.message : 'Network error. Please retry.';
            toggleModal({
                title: 'Network issue',
                message,
                variant: 'error'
            });
        } finally {
            submitButton.disabled = false;
            submitButton.textContent = 'Complete enrollment';
        }
    });

    window.addEventListener('beforeunload', () => streamManager.stop());
}

function initLoginPage() {
    const video = document.getElementById('loginVideo');
    const canvas = document.getElementById('loginCanvas');
    const statusBadge = document.getElementById('loginStatus');
    const instruction = document.getElementById('loginInstruction');
    const attemptChip = document.getElementById('loginAttemptStatus');
    const loginButton = document.getElementById('loginWithFace');
    const restartButton = document.getElementById('loginRestart');
    const stopButton = document.getElementById('loginStop');
    const fallbackForm = document.getElementById('fallbackForm');

    if (!video || !canvas || !loginButton || !attemptChip) {
        return;
    }

    let attempt = 1;
    const maxAttempts = 3;

    async function startCamera(forceRestart = false) {
        if (forceRestart) {
            streamManager.stop();
            setChip(statusBadge, 'Restarting camera...', 'warning');
            setInstruction(instruction, 'Reinitializing camera stream...');
        }
        try {
            await streamManager.start(video);
            setChip(statusBadge, 'Camera ready', 'success');
            setInstruction(instruction, 'Look straight ahead and click authenticate when ready.');
            setChip(attemptChip, `Ready for attempt ${attempt} of ${maxAttempts}`);
        } catch (error) {
            const message = error instanceof Error ? error.message : 'Unable to access camera.';
            setChip(statusBadge, 'Camera blocked', 'error');
            setInstruction(instruction, 'Camera unavailable. Use fallback credentials.');
            toggleModal({
                title: 'Camera permission required',
                message,
                variant: 'warning'
            });
        }
    }

    startCamera();

    restartButton?.addEventListener('click', () => {
        attempt = 1;
        setChip(attemptChip, 'Restarting attempts', 'warning');
        startCamera(true);
    });

    stopButton?.addEventListener('click', () => {
        streamManager.stop();
        setChip(statusBadge, 'Camera stopped', 'warning');
        setInstruction(instruction, 'Camera stopped. Restart to authenticate via face.');
    });

    loginButton.addEventListener('click', async (event) => {
        event.preventDefault();

        const usernameInput = document.getElementById('loginUsername');
        const username = usernameInput ? usernameInput.value.trim() : '';

        if (!username) {
            toggleModal({
                title: 'Username needed',
                message: 'Enter your username before authenticating.',
                variant: 'warning'
            });
            return;
        }

        if (!streamManager.isActive()) {
            toggleModal({
                title: 'Camera inactive',
                message: 'Restart the camera before authenticating with your face.',
                variant: 'warning'
            });
            return;
        }

        let snapshot;
        try {
            snapshot = streamManager.capture(video, canvas);
        } catch (error) {
            const message = error instanceof Error ? error.message : 'Unable to capture frame. Adjust positioning and retry.';
            toggleModal({
                title: 'Capture unavailable',
                message,
                variant: 'warning'
            });
            return;
        }

        setChip(statusBadge, 'Processing...', 'warning');
        setInstruction(instruction, 'Analyzing captured frame for verification...');
        setChip(attemptChip, `Authenticating... attempt ${attempt}/${maxAttempts}`, 'warning');

        loginButton.disabled = true;
        loginButton.textContent = 'Authenticating...';

        try {
            const payload = {
                username,
                usernmae: username,
                face_image: snapshot,
                attempt
            };
            const { ok, status, data } = await submitJSON(apiRoutes.loginFace, payload);
            if (ok) {
                setChip(attemptChip, 'Authenticated successfully', 'success');
                setChip(statusBadge, 'Access granted', 'success');
                setInstruction(instruction, 'Welcome back! Redirecting you now.');
                streamManager.stop();
                // Direct redirect without modal
                setTimeout(() => {
                    window.location.href = '/dashboard';
                }, 500);
            } else if (status === 401 && data?.status === 'retry') {
                attempt = data.attempt || attempt + 1;
                const attemptsLeft = Math.max(maxAttempts - (attempt - 1), 0);
                const baseMessage = data.message || 'Face mismatch detected. Please retry.';
                const variant = attemptsLeft ? 'warning' : 'error';
                const statusText = attemptsLeft ? 'Retry required' : 'Fallback advised';
                setChip(attemptChip, baseMessage, variant);
                setChip(statusBadge, statusText, variant);
                setInstruction(instruction, attemptsLeft ? 'Re-align and try again.' : 'Switch to credential login for now.');
                toggleModal({
                    title: attemptsLeft ? 'Face not recognized' : 'Fallback recommended',
                    message: attemptsLeft ? baseMessage : `${baseMessage} Please use credential login or contact support.`,
                    variant
                });
                if (!attemptsLeft) {
                    streamManager.stop();
                }
            } else {
                const message = data?.message || 'Authentication failed.';
                setChip(attemptChip, message, 'error');
                setChip(statusBadge, 'Authentication failed', 'error');
                setInstruction(instruction, 'Try again or switch to fallback credentials.');
                toggleModal({
                    title: 'Authentication error',
                    message,
                    variant: 'error'
                });
            }
        } catch (error) {
            const message = error instanceof Error ? error.message : 'Network error.';
            setChip(attemptChip, 'Network issue. Try again.', 'error');
            setChip(statusBadge, 'Network error', 'error');
            setInstruction(instruction, 'Network issue detected. Please retry.');
            toggleModal({
                title: 'Network error',
                message,
                variant: 'error'
            });
        } finally {
            loginButton.disabled = false;
            loginButton.textContent = 'Authenticate with face';
        }
    });

    fallbackForm?.addEventListener('submit', async (event) => {
        event.preventDefault();

        const usernameInput = document.getElementById('fallbackUsername');
        const passwordInput = document.getElementById('fallbackPassword');

        const username = usernameInput ? usernameInput.value.trim() : '';
        const password = passwordInput ? passwordInput.value : '';

        if (!username || !password) {
            toggleModal({
                title: 'Incomplete credentials',
                message: 'Enter both username and password to continue.',
                variant: 'warning'
            });
            return;
        }

        const submitButton = fallbackForm.querySelector("button[type='submit']");
        if (!submitButton) {
            return;
        }

        submitButton.disabled = true;
        submitButton.textContent = 'Verifying...';

        try {
            const { ok, data } = await submitJSON(apiRoutes.loginCred, { username, password });
            if (ok) {
                // Direct redirect without modal
                window.location.href = '/dashboard';
            } else {
                const message = data?.message || 'Credentials not recognized.';
                toggleModal({
                    title: 'Login error',
                    message,
                    variant: 'error'
                });
            }
        } catch (error) {
            const message = error instanceof Error ? error.message : 'Network error.';
            toggleModal({
                title: 'Network error',
                message,
                variant: 'error'
            });
        } finally {
            submitButton.disabled = false;
            submitButton.textContent = 'Login with credentials';
        }
    });

    window.addEventListener('beforeunload', () => streamManager.stop());
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            streamManager.stop();
        }
    });
}

function bootstrap() {
    setupNavigation();
    setupRevealAnimations();
    registerModalHandlers();

    if (currentPage === 'register') {
        initRegisterPage();
    }
    if (currentPage === 'login') {
        initLoginPage();
    }

    window.addEventListener('pagehide', () => streamManager.stop());
}

document.addEventListener('DOMContentLoaded', bootstrap);
})();
