/**
 * Utilidades generales para la aplicación
 */
const Utils = {
    
    /**
     * Formatear distancia
     */
    formatDistance(distanceKm) {
        if (distanceKm < 1) {
            return `${Math.round(distanceKm * 1000)} m`;
        }
        return `${distanceKm.toFixed(1)} km`;
    },
    
    /**
     * Formatear peso
     */
    formatWeight(weightKg) {
        if (weightKg < 1000) {
            return `${weightKg.toFixed(1)} kg`;
        }
        return `${(weightKg / 1000).toFixed(1)} t`;
    },
    
    /**
     * Formatear tiempo
     */
    formatTime(timeHours) {
        if (timeHours < 1) {
            const minutes = Math.round(timeHours * 60);
            return `${minutes} min`;
        }
        
        const hours = Math.floor(timeHours);
        const minutes = Math.round((timeHours - hours) * 60);
        
        if (minutes > 0) {
            return `${hours}h ${minutes}min`;
        }
        return `${hours}h`;
    },
    
    /**
     * Capitalizar primera letra
     */
    capitalize(str) {
        if (!str) return '';
        return str.charAt(0).toUpperCase() + str.slice(1);
    },
    
    /**
     * Validar coordenadas
     */
    isValidCoordinate(lat, lng) {
        return lat >= -90 && lat <= 90 && lng >= -180 && lng <= 180;
    },
    
    /**
     * Generar ID único
     */
    generateId(prefix = 'id') {
        return `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    },
    
    /**
     * Debounce function
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    /**
     * Throttle function
     */
    throttle(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },
    
    /**
     * Validar email
     */
    isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },
    
    /**
     * Formatear número con separadores de miles
     */
    formatNumber(num) {
        return new Intl.NumberFormat('es-MX').format(num);
    },
    
    /**
     * Calcular porcentaje
     */
    calculatePercentage(part, total) {
        if (total === 0) return 0;
        return Math.round((part / total) * 100);
    },
    
    /**
     * Truncar texto
     */
    truncateText(text, maxLength = 50) {
        if (!text || text.length <= maxLength) return text;
        return text.substring(0, maxLength - 3) + '...';
    },
    
    /**
     * Obtener color de ruta por índice
     */
    getRouteColor(index) {
        const colors = AppConfig.colors.routes;
        return colors[index % colors.length];
    },
    
    /**
     * Crear elemento DOM
     */
    createElement(tag, className, content) {
        const element = document.createElement(tag);
        if (className) element.className = className;
        if (content) element.innerHTML = content;
        return element;
    },
    
    /**
     * Mostrar/ocultar elemento
     */
    toggleElement(element, show) {
        if (show === undefined) {
            element.style.display = element.style.display === 'none' ? '' : 'none';
        } else {
            element.style.display = show ? '' : 'none';
        }
    },
    
    /**
     * Animar elemento con fade
     */
    fadeIn(element, duration = 300) {
        element.style.opacity = '0';
        element.style.display = '';
        
        const start = performance.now();
        
        function animate(currentTime) {
            const elapsed = currentTime - start;
            const progress = Math.min(elapsed / duration, 1);
            
            element.style.opacity = progress;
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        }
        
        requestAnimationFrame(animate);
    },
    
    /**
     * Animar elemento con fade out
     */
    fadeOut(element, duration = 300) {
        const start = performance.now();
        const startOpacity = parseFloat(getComputedStyle(element).opacity);
        
        function animate(currentTime) {
            const elapsed = currentTime - start;
            const progress = Math.min(elapsed / duration, 1);
            
            element.style.opacity = startOpacity * (1 - progress);
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                element.style.display = 'none';
            }
        }
        
        requestAnimationFrame(animate);
    },
    
    /**
     * Validar formulario
     */
    validateForm(formElement) {
        const inputs = formElement.querySelectorAll('input[required], select[required]');
        let isValid = true;
        
        inputs.forEach(input => {
            if (!input.value.trim()) {
                input.classList.add('error');
                isValid = false;
            } else {
                input.classList.remove('error');
            }
        });
        
        return isValid;
    },
    
    /**
     * Parsear parámetros de URL
     */
    parseUrlParams() {
        const params = new URLSearchParams(window.location.search);
        const result = {};
        
        for (const [key, value] of params) {
            result[key] = value;
        }
        
        return result;
    },
    
    /**
     * Copiar texto al portapapeles
     */
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            return true;
        } catch (err) {
            // Fallback para navegadores antiguos
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            const success = document.execCommand('copy');
            document.body.removeChild(textArea);
            return success;
        }
    },
    
    /**
     * Descargar archivo
     */
    downloadFile(content, filename, contentType = 'text/plain') {
        const blob = new Blob([content], { type: contentType });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        link.click();
        URL.revokeObjectURL(url);
    },
    
    /**
     * Convertir objeto a JSON formateado
     */
    formatJSON(obj) {
        return JSON.stringify(obj, null, 2);
    }
};

// Hacer Utils global
window.Utils = Utils;