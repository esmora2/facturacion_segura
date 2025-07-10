/**
 * Ejemplo de uso del endpoint /api/auth/validate-password/ desde el frontend
 * Sistema de Facturación Segura
 */

// Configuración base de la API
const API_BASE_URL = 'http://localhost:8000';
const API_ENDPOINTS = {
    validatePassword: '/api/auth/validate-password/',
    token: '/api/token/',
    me: '/api/me/'
};

/**
 * Clase para manejar la validación de contraseñas
 */
class PasswordValidator {
    constructor(token) {
        this.token = token;
        this.headers = {
            'Content-Type': 'application/json',
            'Authorization': `Token ${token}`
        };
    }

    /**
     * Validar la contraseña del usuario autenticado
     * @param {string} password - Contraseña a validar
     * @returns {Promise<Object>} Resultado de la validación
     */
    async validatePassword(password) {
        try {
            const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.validatePassword}`, {
                method: 'POST',
                headers: this.headers,
                body: JSON.stringify({ password })
            });

            const data = await response.json();

            if (response.ok) {
                return {
                    success: true,
                    valid: data.valid,
                    message: data.message,
                    user: data.user
                };
            } else {
                return {
                    success: false,
                    valid: false,
                    error: data.error || 'Error desconocido'
                };
            }
        } catch (error) {
            return {
                success: false,
                valid: false,
                error: `Error de conexión: ${error.message}`
            };
        }
    }

    /**
     * Mostrar modal de confirmación de contraseña
     * @param {string} action - Acción que se va a realizar
     * @returns {Promise<boolean>} true si la contraseña es válida
     */
    async showPasswordConfirmationModal(action = 'realizar esta acción') {
        return new Promise((resolve) => {
            // Crear modal dinámicamente
            const modal = document.createElement('div');
            modal.innerHTML = `
                <div class="modal-overlay" style="
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(0,0,0,0.5);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    z-index: 1000;
                ">
                    <div class="modal-content" style="
                        background: white;
                        padding: 20px;
                        border-radius: 8px;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                        max-width: 400px;
                        width: 90%;
                    ">
                        <h3 style="margin-top: 0; color: #d32f2f;">Confirmar Acción</h3>
                        <p>Para ${action}, por favor ingresa tu contraseña:</p>
                        <input type="password" id="confirmPassword" placeholder="Tu contraseña" style="
                            width: 100%;
                            padding: 10px;
                            margin: 10px 0;
                            border: 1px solid #ddd;
                            border-radius: 4px;
                            box-sizing: border-box;
                        ">
                        <div id="passwordError" style="color: #d32f2f; margin: 5px 0; display: none;"></div>
                        <div style="text-align: right; margin-top: 15px;">
                            <button id="cancelBtn" style="
                                background: #f5f5f5;
                                border: 1px solid #ddd;
                                padding: 8px 16px;
                                margin-right: 10px;
                                border-radius: 4px;
                                cursor: pointer;
                            ">Cancelar</button>
                            <button id="confirmBtn" style="
                                background: #1976d2;
                                color: white;
                                border: none;
                                padding: 8px 16px;
                                border-radius: 4px;
                                cursor: pointer;
                            ">Confirmar</button>
                        </div>
                    </div>
                </div>
            `;

            document.body.appendChild(modal);

            const passwordInput = modal.querySelector('#confirmPassword');
            const errorDiv = modal.querySelector('#passwordError');
            const cancelBtn = modal.querySelector('#cancelBtn');
            const confirmBtn = modal.querySelector('#confirmBtn');

            // Enfocar el input
            setTimeout(() => passwordInput.focus(), 100);

            // Función para limpiar el modal
            const cleanup = () => {
                document.body.removeChild(modal);
            };

            // Manejar cancelación
            cancelBtn.addEventListener('click', () => {
                cleanup();
                resolve(false);
            });

            // Manejar confirmación
            const handleConfirm = async () => {
                const password = passwordInput.value;
                
                if (!password) {
                    errorDiv.textContent = 'Por favor ingresa tu contraseña';
                    errorDiv.style.display = 'block';
                    return;
                }

                // Deshabilitar botón durante validación
                confirmBtn.disabled = true;
                confirmBtn.textContent = 'Validando...';

                try {
                    const result = await this.validatePassword(password);
                    
                    if (result.success && result.valid) {
                        cleanup();
                        resolve(true);
                    } else {
                        errorDiv.textContent = result.error || 'Contraseña incorrecta';
                        errorDiv.style.display = 'block';
                        confirmBtn.disabled = false;
                        confirmBtn.textContent = 'Confirmar';
                        passwordInput.select();
                    }
                } catch (error) {
                    errorDiv.textContent = 'Error de conexión';
                    errorDiv.style.display = 'block';
                    confirmBtn.disabled = false;
                    confirmBtn.textContent = 'Confirmar';
                }
            };

            confirmBtn.addEventListener('click', handleConfirm);
            
            // Permitir confirmar con Enter
            passwordInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    handleConfirm();
                }
            });

            // Cerrar con Escape
            document.addEventListener('keydown', function escapeHandler(e) {
                if (e.key === 'Escape') {
                    document.removeEventListener('keydown', escapeHandler);
                    cleanup();
                    resolve(false);
                }
            });
        });
    }
}

/**
 * Ejemplo de uso con diferentes operaciones críticas
 */
class CriticalOperations {
    constructor(token) {
        this.passwordValidator = new PasswordValidator(token);
    }

    /**
     * Eliminar factura con confirmación de contraseña
     */
    async deleteFactura(facturaId) {
        const confirmed = await this.passwordValidator.showPasswordConfirmationModal(
            'eliminar permanentemente esta factura'
        );

        if (!confirmed) {
            console.log('Operación cancelada por el usuario');
            return false;
        }

        try {
            // Aquí iría la lógica para eliminar la factura
            const response = await fetch(`${API_BASE_URL}/api/facturas/${facturaId}/`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Token ${this.passwordValidator.token}`
                }
            });

            if (response.ok) {
                alert('Factura eliminada exitosamente');
                return true;
            } else {
                alert('Error al eliminar la factura');
                return false;
            }
        } catch (error) {
            alert(`Error: ${error.message}`);
            return false;
        }
    }

    /**
     * Eliminar cliente con confirmación de contraseña
     */
    async deleteCliente(clienteId) {
        const confirmed = await this.passwordValidator.showPasswordConfirmationModal(
            'eliminar permanentemente este cliente'
        );

        if (!confirmed) {
            return false;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/api/clientes/${clienteId}/`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Token ${this.passwordValidator.token}`
                }
            });

            return response.ok;
        } catch (error) {
            console.error('Error al eliminar cliente:', error);
            return false;
        }
    }

    /**
     * Cambiar configuraciones críticas del sistema
     */
    async changeCriticalSettings(settings) {
        const confirmed = await this.passwordValidator.showPasswordConfirmationModal(
            'cambiar la configuración crítica del sistema'
        );

        if (!confirmed) {
            return false;
        }

        // Lógica para cambiar configuraciones...
        console.log('Configuraciones cambiadas:', settings);
        return true;
    }
}

/**
 * Ejemplo de uso directo del endpoint
 */
async function ejemploUsoDirecto() {
    // Obtener token (ejemplo)
    const token = localStorage.getItem('authToken');
    
    if (!token) {
        console.error('No hay token de autenticación');
        return;
    }

    const validator = new PasswordValidator(token);

    // Validar contraseña directamente
    const password = prompt('Ingresa tu contraseña:');
    if (password) {
        const result = await validator.validatePassword(password);
        
        if (result.success && result.valid) {
            console.log('✅ Contraseña válida:', result.user);
            alert('Contraseña válida! Puedes proceder.');
        } else {
            console.log('❌ Contraseña inválida:', result.error);
            alert(`Error: ${result.error}`);
        }
    }
}

/**
 * Ejemplo de integración con formularios
 */
function setupCriticalOperationButtons() {
    const token = localStorage.getItem('authToken');
    if (!token) return;

    const operations = new CriticalOperations(token);

    // Configurar botones de eliminación
    document.querySelectorAll('[data-delete-factura]').forEach(button => {
        button.addEventListener('click', async (e) => {
            e.preventDefault();
            const facturaId = button.dataset.deleteFactura;
            await operations.deleteFactura(facturaId);
        });
    });

    document.querySelectorAll('[data-delete-cliente]').forEach(button => {
        button.addEventListener('click', async (e) => {
            e.preventDefault();
            const clienteId = button.dataset.deleteCliente;
            await operations.deleteCliente(clienteId);
        });
    });
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', setupCriticalOperationButtons);

// Exportar para uso en módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { PasswordValidator, CriticalOperations };
}
