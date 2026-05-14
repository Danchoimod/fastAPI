document.addEventListener('DOMContentLoaded', () => {
    const loginContainer = document.getElementById('login-container');
    const registerContainer = document.getElementById('register-container');
    const showRegister = document.getElementById('show-register');
    const showLogin = document.getElementById('show-login');
    const messageDiv = document.getElementById('message');

    function showMessage(text, isError = false) {
        messageDiv.textContent = text;
        messageDiv.classList.remove('hidden', 'bg-green-500/10', 'text-green-400', 'border-green-500/20', 'bg-red-500/10', 'text-red-400', 'border-red-500/20');
        
        if (isError) {
            messageDiv.classList.add('bg-red-500/10', 'text-red-400', 'border-red-500/20');
        } else {
            messageDiv.classList.add('bg-green-500/10', 'text-green-400', 'border-green-500/20');
        }
        
        messageDiv.classList.remove('hidden');
        
        setTimeout(() => {
            messageDiv.classList.add('hidden');
        }, 5000);
    }

    showRegister.addEventListener('click', (e) => {
        e.preventDefault();
        loginContainer.classList.add('hidden');
        registerContainer.classList.remove('hidden');
        messageDiv.classList.add('hidden');
    });

    showLogin.addEventListener('click', (e) => {
        e.preventDefault();
        registerContainer.classList.add('hidden');
        loginContainer.classList.remove('hidden');
        messageDiv.classList.add('hidden');
    });

    document.getElementById('login-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('login-username').value;
        const password = document.getElementById('login-password').value;

        try {
            const response = await fetch('/api/v1/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();
            if (response.ok) {
                showMessage('Login successful! Welcome, ' + data.user);
            } else {
                showMessage(data.detail || 'Login failed', true);
            }
        } catch (err) {
            showMessage('An error occurred', true);
        }
    });

    document.getElementById('register-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('reg-username').value;
        const email = document.getElementById('reg-email').value;
        const password = document.getElementById('reg-password').value;

        try {
            const response = await fetch('/api/v1/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, password })
            });

            const data = await response.json();
            if (response.ok) {
                showMessage('Registration successful! You can now sign in.');
                setTimeout(() => showLogin.click(), 1500);
            } else {
                showMessage(data.detail || 'Registration failed', true);
            }
        } catch (err) {
            showMessage('An error occurred', true);
        }
    });
});
