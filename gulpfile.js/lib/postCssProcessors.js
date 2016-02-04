module.exports = [
  // Sassy based plugins
  require('postcss-import')({
    glob: true
  }),
  require('postcss-sassy-mixins'),
  require('postcss-advanced-variables'),
  require('postcss-custom-selectors'),
  require('postcss-custom-media'),
  require('postcss-custom-properties'),
  require('postcss-color-function'),
  require('postcss-nested'),
  require('postcss-atroot'),
  require('postcss-property-lookup'),
  require('postcss-selector-matches'),
  require('postcss-selector-not'),
  require('postcss-functions')({
    functions: {
      percentage: function(val1, val2) {
        var number = (val1 / val2) * 100

        return number.toFixed(2) + '%'
      }
    }
  }),
  require('postcss-map')({
    basePath: 'rocket_league/assets/css/config',
    maps: ['breakpoints.yaml', 'colors.yaml', 'fonts.yaml', 'grid.yaml', 'misc.yaml']
  }),
  require('postcss-calc'),
  require('postcss-conditionals'),

  // Niceties
  require('postcss-assets')({
    basePath: 'rocket_league/assets/',
    loadPaths: ['img/'],
    baseUrl: '/static/'
  }),
  require('postcss-brand-colors'),
  require('postcss-fakeid'),
  require('postcss-flexbugs-fixes'),
  require('postcss-property-lookup'),
  require('postcss-pxtorem'),
  require('postcss-quantity-queries'),
  require('postcss-will-change'),
  require('autoprefixer')({
    browsers: ['last 2 versions', 'IE 9', 'IE 10']
  }),
];
