import { format as formatUrl } from 'url';
import { readFileSync as readFile } from 'fs';
import { defaults } from 'lodash';
import { props } from 'bluebird';
import Boom from 'boom';
import { resolve } from 'path';
import fromRoot from '../utils/from_root';
import UiExports from './ui_exports';
import UiBundle from './ui_bundle';
import UiBundleCollection from './ui_bundle_collection';
import UiBundlerEnv from './ui_bundler_env';

export default async (kbnServer, server, config) => {

  const loadingGif = readFile(fromRoot('src/ui/public/loading.gif'), { encoding: 'base64'});

  const uiExports = kbnServer.uiExports = new UiExports({
    urlBasePath: config.get('server.basePath')
  });

  const bundlerEnv = new UiBundlerEnv(config.get('optimize.bundleDir'));
  bundlerEnv.addContext('env', config.get('env.name'));
  bundlerEnv.addContext('urlBasePath', config.get('server.basePath'));
  bundlerEnv.addContext('sourceMaps', config.get('optimize.sourceMaps'));
  bundlerEnv.addContext('kbnVersion', config.get('pkg.version'));
  bundlerEnv.addContext('buildNum', config.get('pkg.buildNum'));
  uiExports.addConsumer(bundlerEnv);

  for (let plugin of kbnServer.plugins) {
    uiExports.consumePlugin(plugin);
  }

  const bundles = kbnServer.bundles = new UiBundleCollection(bundlerEnv, config.get('optimize.bundleFilter'));

  for (let app of uiExports.getAllApps()) {
    bundles.addApp(app);
  }

  for (let gen of uiExports.getBundleProviders()) {
    const bundle = await gen(UiBundle, bundlerEnv, uiExports.getAllApps(), kbnServer.plugins);
    if (bundle) bundles.add(bundle);
  }

  // render all views from the ui/views directory
  server.setupViews(resolve(__dirname, 'views'));
  server.exposeStaticFile('/loading.gif', resolve(__dirname, 'public/loading.gif'));

  server.route({
    path: '/app/{id}',
    method: 'GET',
    handler: function (req, reply) {
      const id = req.params.id;
      const app = uiExports.apps.byId[id];
      if (!app) return reply(Boom.notFound('Unknown app ' + id));

      if (kbnServer.status.isGreen()) {
        return reply.renderApp(app);
      } else {
        return reply.renderStatusPage();
      }
    }
  });

  async function getKibanaPayload({ app, request, includeUserProvidedConfig }) {
    const uiSettings = server.uiSettings();
    return {
      app: app,
      nav: uiExports.navLinks.inOrder,
      version: kbnServer.version,
      buildNum: config.get('pkg.buildNum'),
      buildSha: config.get('pkg.buildSha'),
      basePath: config.get('server.basePath'),
      serverName: config.get('server.name'),
      uiSettings: await props({
        defaults: uiSettings.getDefaults(),
        user: includeUserProvidedConfig && uiSettings.getUserProvided(request)
      }),
      vars: defaults(app.getInjectedVars() || {}, uiExports.defaultInjectedVars),
    };
  }

  async function renderApp({ app, reply, includeUserProvidedConfig = true }) {
    try {
      return reply.view(app.templateName, {
        app,
        loadingGif: loadingGif,
        kibanaPayload: await getKibanaPayload({
          app,
          request: reply.request,
          includeUserProvidedConfig
        }),
        bundlePath: `${config.get('server.basePath')}/bundles`,
      });
    } catch (err) {
      reply(err);
    }
  }

  server.decorate('reply', 'renderApp', function (app) {
    return renderApp({
      app,
      reply: this,
      includeUserProvidedConfig: true,
    });
  });

  server.decorate('reply', 'renderAppWithDefaultConfig', function (app) {
    return renderApp({
      app,
      reply: this,
      includeUserProvidedConfig: false,
    });
  });
};
