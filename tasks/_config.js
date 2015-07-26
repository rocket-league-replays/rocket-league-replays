const staticFolder = 'rocket_league/static';
const templateFolder = 'rocket_league/templates';

export default {
  bower: {
    path: 'bower_components'
  },
  css: {
    path: `${staticFolder}/css`
  },
  images: {
    path: `${staticFolder}/images`,
    src: [
      `${staticFolder}/images/**/*`
    ]
  },
  js: {
    path: `${staticFolder}/js`,
    src: [
      `${staticFolder}/*.js`,
      `${staticFolder}/**/*.js`
    ]
  },
  html: {
    path: templateFolder,
    src: [
      `${templateFolder}/*.html`,
      `${templateFolder}/**/*.html`
    ]
  },
  sass: {
    path: `${staticFolder}/scss`,
    src: [
      `${staticFolder}/scss/*.scss`,
      `${staticFolder}/scss/**/*.scss`
    ]
  },
  temp: {
    path: `.tmp`,
    css: `.tmp/styles`
  },
  watchify: {
    fileIn: `${staticFolder}/js/src/main.js`,
    fileOut: `app.js`,
    folderIn: `${staticFolder}/js/src`,
    folderOut: `${staticFolder}/js/build`
  }
};
