// Stealth script for antidetect browser
// This script patches browser APIs to provide consistent fingerprints

(function() {
    'use strict';

    // Configuration will be injected by Python
    const CONFIG = {
        userAgent: '{{USER_AGENT}}',
        platform: '{{PLATFORM}}',
        vendor: '{{VENDOR}}',
        languages: {{LANGUAGES}},
        hardwareConcurrency: {{HARDWARE_CONCURRENCY}},
        deviceMemory: {{DEVICE_MEMORY}},
        maxTouchPoints: {{MAX_TOUCH_POINTS}},
        screenWidth: {{SCREEN_WIDTH}},
        screenHeight: {{SCREEN_HEIGHT}},
        colorDepth: {{COLOR_DEPTH}},
        pixelRatio: {{PIXEL_RATIO}},
        timezone: '{{TIMEZONE}}',
        timezoneOffset: {{TIMEZONE_OFFSET}},
        webglVendor: '{{WEBGL_VENDOR}}',
        webglRenderer: '{{WEBGL_RENDERER}}',
        plugins: {{PLUGINS}},
        latitude: {{LATITUDE}},
        longitude: {{LONGITUDE}}
    };

    // ==================== Navigator Patches ====================

    // Override userAgent
    Object.defineProperty(navigator, 'userAgent', {
        get: () => CONFIG.userAgent,
        configurable: true
    });

    // Override platform
    Object.defineProperty(navigator, 'platform', {
        get: () => CONFIG.platform,
        configurable: true
    });

    // Override vendor
    Object.defineProperty(navigator, 'vendor', {
        get: () => CONFIG.vendor,
        configurable: true
    });

    // Override languages
    Object.defineProperty(navigator, 'languages', {
        get: () => Object.freeze([...CONFIG.languages]),
        configurable: true
    });

    Object.defineProperty(navigator, 'language', {
        get: () => CONFIG.languages[0],
        configurable: true
    });

    // Override hardwareConcurrency
    Object.defineProperty(navigator, 'hardwareConcurrency', {
        get: () => CONFIG.hardwareConcurrency,
        configurable: true
    });

    // Override deviceMemory
    Object.defineProperty(navigator, 'deviceMemory', {
        get: () => CONFIG.deviceMemory,
        configurable: true
    });

    // Override maxTouchPoints
    Object.defineProperty(navigator, 'maxTouchPoints', {
        get: () => CONFIG.maxTouchPoints,
        configurable: true
    });

    // ==================== Screen Patches ====================

    Object.defineProperty(screen, 'width', {
        get: () => CONFIG.screenWidth,
        configurable: true
    });

    Object.defineProperty(screen, 'height', {
        get: () => CONFIG.screenHeight,
        configurable: true
    });

    Object.defineProperty(screen, 'availWidth', {
        get: () => CONFIG.screenWidth,
        configurable: true
    });

    Object.defineProperty(screen, 'availHeight', {
        get: () => CONFIG.screenHeight - 40, // Taskbar
        configurable: true
    });

    Object.defineProperty(screen, 'colorDepth', {
        get: () => CONFIG.colorDepth,
        configurable: true
    });

    Object.defineProperty(screen, 'pixelDepth', {
        get: () => CONFIG.colorDepth,
        configurable: true
    });

    Object.defineProperty(window, 'devicePixelRatio', {
        get: () => CONFIG.pixelRatio,
        configurable: true
    });

    Object.defineProperty(window, 'innerWidth', {
        get: () => CONFIG.screenWidth,
        configurable: true
    });

    Object.defineProperty(window, 'innerHeight', {
        get: () => CONFIG.screenHeight - 140, // Browser UI
        configurable: true
    });

    Object.defineProperty(window, 'outerWidth', {
        get: () => CONFIG.screenWidth,
        configurable: true
    });

    Object.defineProperty(window, 'outerHeight', {
        get: () => CONFIG.screenHeight,
        configurable: true
    });

    // ==================== Timezone Patches ====================

    // Override Date.prototype.getTimezoneOffset
    const originalGetTimezoneOffset = Date.prototype.getTimezoneOffset;
    Date.prototype.getTimezoneOffset = function() {
        return CONFIG.timezoneOffset;
    };

    // Override Intl.DateTimeFormat
    const originalDateTimeFormat = Intl.DateTimeFormat;
    const originalResolvedOptions = Intl.DateTimeFormat.prototype.resolvedOptions;

    Intl.DateTimeFormat = function(...args) {
        if (args.length === 0 || (args[0] === undefined && args[1] === undefined)) {
            args[1] = { timeZone: CONFIG.timezone };
        } else if (args[1] && !args[1].timeZone) {
            args[1].timeZone = CONFIG.timezone;
        }
        return new originalDateTimeFormat(...args);
    };

    Intl.DateTimeFormat.prototype = originalDateTimeFormat.prototype;
    Intl.DateTimeFormat.prototype.resolvedOptions = function() {
        const options = originalResolvedOptions.call(this);
        options.timeZone = CONFIG.timezone;
        return options;
    };

    // ==================== WebGL Patches ====================

    const getParameterProxy = function(target, param) {
        // UNMASKED_VENDOR_WEBGL
        if (param === 37445) {
            return CONFIG.webglVendor;
        }
        // UNMASKED_RENDERER_WEBGL
        if (param === 37446) {
            return CONFIG.webglRenderer;
        }
        return target.call(this, param);
    };

    // Patch WebGLRenderingContext
    const webglGetParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(param) {
        return getParameterProxy.call(this, webglGetParameter, param);
    };

    // Patch WebGL2RenderingContext if available
    if (typeof WebGL2RenderingContext !== 'undefined') {
        const webgl2GetParameter = WebGL2RenderingContext.prototype.getParameter;
        WebGL2RenderingContext.prototype.getParameter = function(param) {
            return getParameterProxy.call(this, webgl2GetParameter, param);
        };
    }

    // ==================== Canvas Patches ====================

    // Add noise to canvas to prevent fingerprinting
    const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
    HTMLCanvasElement.prototype.toDataURL = function(type, quality) {
        const context = this.getContext('2d');
        if (context) {
            const imageData = context.getImageData(0, 0, this.width, this.height);
            const data = imageData.data;
            // Add subtle noise
            for (let i = 0; i < data.length; i += 4) {
                // Only modify every 10th pixel slightly
                if (i % 40 === 0) {
                    data[i] = data[i] ^ (Math.random() > 0.5 ? 1 : 0);
                }
            }
            context.putImageData(imageData, 0, 0);
        }
        return originalToDataURL.call(this, type, quality);
    };

    const originalToBlob = HTMLCanvasElement.prototype.toBlob;
    HTMLCanvasElement.prototype.toBlob = function(callback, type, quality) {
        const context = this.getContext('2d');
        if (context) {
            const imageData = context.getImageData(0, 0, this.width, this.height);
            const data = imageData.data;
            for (let i = 0; i < data.length; i += 4) {
                if (i % 40 === 0) {
                    data[i] = data[i] ^ (Math.random() > 0.5 ? 1 : 0);
                }
            }
            context.putImageData(imageData, 0, 0);
        }
        return originalToBlob.call(this, callback, type, quality);
    };

    // ==================== Plugins Patches ====================

    // Create fake plugins
    const createPlugin = (name, filename, description) => ({
        name,
        filename,
        description,
        length: 1,
        item: () => null,
        namedItem: () => null,
        [Symbol.iterator]: function* () { yield this; }
    });

    const fakePlugins = CONFIG.plugins.map((name, i) =>
        createPlugin(name, `internal-${name.toLowerCase().replace(/\s+/g, '-')}-viewer`, name)
    );

    Object.defineProperty(navigator, 'plugins', {
        get: () => {
            const plugins = Object.create(PluginArray.prototype);
            fakePlugins.forEach((plugin, i) => {
                plugins[i] = plugin;
            });
            Object.defineProperty(plugins, 'length', { value: fakePlugins.length });
            plugins.item = (i) => plugins[i] || null;
            plugins.namedItem = (name) => fakePlugins.find(p => p.name === name) || null;
            plugins.refresh = () => {};
            return plugins;
        },
        configurable: true
    });

    // ==================== WebDriver Detection ====================

    // Hide webdriver
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined,
        configurable: true
    });

    // Remove automation-related properties
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;

    // ==================== Permission Patches ====================

    // Override Permissions API
    const originalQuery = navigator.permissions.query;
    navigator.permissions.query = async function(parameters) {
        if (parameters.name === 'notifications') {
            return { state: 'denied', onchange: null };
        }
        return originalQuery.call(this, parameters);
    };

    // ==================== Geolocation Patches ====================

    if (CONFIG.latitude && CONFIG.longitude) {
        const originalGetCurrentPosition = navigator.geolocation.getCurrentPosition;
        navigator.geolocation.getCurrentPosition = function(success, error, options) {
            success({
                coords: {
                    latitude: CONFIG.latitude,
                    longitude: CONFIG.longitude,
                    accuracy: 100,
                    altitude: null,
                    altitudeAccuracy: null,
                    heading: null,
                    speed: null
                },
                timestamp: Date.now()
            });
        };

        const originalWatchPosition = navigator.geolocation.watchPosition;
        navigator.geolocation.watchPosition = function(success, error, options) {
            success({
                coords: {
                    latitude: CONFIG.latitude,
                    longitude: CONFIG.longitude,
                    accuracy: 100,
                    altitude: null,
                    altitudeAccuracy: null,
                    heading: null,
                    speed: null
                },
                timestamp: Date.now()
            });
            return 1;
        };
    }

    // ==================== Battery API ====================

    // Hide battery status (privacy)
    if (navigator.getBattery) {
        navigator.getBattery = async function() {
            return {
                charging: true,
                chargingTime: 0,
                dischargingTime: Infinity,
                level: 1,
                addEventListener: () => {},
                removeEventListener: () => {}
            };
        };
    }

    // ==================== Chrome Detection ====================

    // Add chrome object for Chrome detection
    if (!window.chrome) {
        window.chrome = {
            runtime: {},
            loadTimes: function() {},
            csi: function() {},
            app: {}
        };
    }

    // ==================== Console Warning ====================

    // Prevent console detection
    const originalConsole = window.console;
    window.console = {
        ...originalConsole,
        debug: () => {},
        profile: () => {},
        profileEnd: () => {}
    };

    console.log('[Stealth] Browser fingerprint applied successfully');

})();
