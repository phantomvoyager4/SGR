const fs = require("fs");
const path = require("path");
const evalSourceMapMiddleware = require("react-dev-utils/evalSourceMapMiddleware");
const noopServiceWorkerMiddleware = require("react-dev-utils/noopServiceWorkerMiddleware");
const redirectServedPathMiddleware = require("react-dev-utils/redirectServedPathMiddleware");
const paths = require("react-scripts/config/paths");

module.exports = {
  webpack: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  devServer: (devServerConfig) => {
    // react-scripts 5 still sets the webpack-dev-server 4 onBeforeSetupMiddleware/
    // onAfterSetupMiddleware options, which are deprecated in favor of setupMiddlewares.
    // Re-register the same middleware (source-map click-to-editor support, proxy setup,
    // served-path redirect, and the dev no-op service worker) through setupMiddlewares
    // instead of dropping them, so behavior is unchanged and the warnings go away.
    delete devServerConfig.onBeforeSetupMiddleware;
    delete devServerConfig.onAfterSetupMiddleware;

    devServerConfig.setupMiddlewares = (middlewares, devServer) => {
      if (!devServer) {
        throw new Error("webpack-dev-server is not defined");
      }

      devServer.app.use(evalSourceMapMiddleware(devServer));
      if (fs.existsSync(paths.proxySetup)) {
        require(paths.proxySetup)(devServer.app);
      }

      middlewares.push(
        redirectServedPathMiddleware(paths.publicUrlOrPath),
        noopServiceWorkerMiddleware(paths.publicUrlOrPath)
      );

      return middlewares;
    };

    return devServerConfig;
  },
};
