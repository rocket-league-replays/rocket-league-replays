module.exports = {
  'plugins': [
    'stylelint-statement-max-nesting-depth'
  ],
  'rules': {
    // Plugins
    'statement-max-nesting-depth': [3, {
      countAtRules: false,
      countedNestedAtRules: false
    }],

    // String
    'string-quotes': 'single',

    // Color
    'color-hex-case': 'lower',
    'color-hex-length': 'short',
    'color-named': 'never',
    'color-no-invalid-hex': true,

    // Font
    'font-family-name-quotes': 'single-where-required',
    'font-weight-notation': 'numeric',

    // Number
    'number-leading-zero': 'always',
    'number-max-precision': 3,
    'number-no-trailing-zeros': true,
    'number-zero-length-no-unit': true,

    // Function
    'function-calc-no-unspaced-operator': true,
    'function-comma-space-after': 'always',
    'function-comma-space-before': 'never',
    'function-linear-gradient-no-nonstandard-direction': true,

    // Time
    'time-no-imperceptible': true,

    // Value list
    'value-list-comma-space-after': 'always',
    'value-list-comma-space-before': 'never',

    // Unit
    'unit-blacklist': ['rem'], // Disallow these because PostCSS adds them

    // Declaration
    'declaration-bang-space-after': 'never',
    'declaration-bang-space-before': 'always',
    'declaration-colon-space-after': 'always',
    'declaration-colon-space-before': 'never',
    'declaration-no-important': true,
    'declaration-block-no-duplicate-properties': true,
    'declaration-block-properties-order': [
      {
        emptyLineBefore: 'always',
        properties: [
          'content'
        ]
      },
      {
        emptyLineBefore: 'always',
        properties: [
          'position',
          'top',
          'right',
          'bottom',
          'left',
          'z-index'
        ]
      },
      {
        emptyLineBefore: 'always',
        properties: [
          'align-content',
          'align-items',
          'align-self',
          'flex',
          'flex-basis',
          'flex-direction',
          'flex-flow',
          'flex-grow',
          'flex-shrink',
          'flex-wrap',
          'justify-content',
          'order'
        ]
      },
      {
        emptyLineBefore: 'always',
        properties: [
          'display',
          'max-width',
          'max-height',
          'min-width',
          'min-height',
          'width',
          'height',
          'clear',
          'float',
          'margin',
          'margin-top',
          'margin-right',
          'margin-bottom',
          'margin-left',
          'padding',
          'padding-top',
          'padding-right',
          'padding-bottom',
          'padding-left',
          'table-layout'
        ]
      },
      {
        emptyLineBefore: 'always',
        properties: [
          'font-family',
          'font-size',
          'font-style',
          'font-weight',
          'letter-spacing',
          'line-height',
          'text-align',
          'text-decoration',
          'text-overflow',
          'text-transform'
        ]
      },
      {
        emptyLineBefore: 'always',
        properties: [
          'appearance',
          'background',
          'background-attachment',
          'background-blend-mode',
          'background-color',
          'background-image',
          'background-position',
          'background-repeat',
          'background-size',
          'border',
          'border-top',
          'border-right',
          'border-bottom',
          'border-left',
          'border-radius',
          'border-top-left-radius',
          'border-top-right-radius',
          'border-bottom-right-radius',
          'border-bottom-left-radius',
          'box-shadow',
          'color',
          'cursor',
          'mix-blend-mode',
          'opacity',
          'overflow',
          'overflow-x',
          'overflow-y',
          'visibility'
        ]
      },
      {
        emptyLineBefore: 'always',
        properties: [
          'animation',
          'animation-delay',
          'animation-direction',
          'animation-duration',
          'animation-fill-mode',
          'animation-iteration-count',
          'animation-name',
          'animation-play-state',
          'animation-timing-function',
          'transform',
          'transition'
        ]
      }
    ],

    // Declaration block
    'declaration-block-semicolon-newline-after': 'always-multi-line',
    'declaration-block-semicolon-space-after': 'always-single-line',

    // Block
    'block-closing-brace-newline-before': 'always-multi-line',
    'block-closing-brace-space-before': 'always-single-line',
    'block-no-empty': true,
    'block-opening-brace-newline-after': 'always-multi-line',
    'block-opening-brace-space-after': 'always-single-line',
    'block-opening-brace-space-before': 'always',

    // Selector
    'selector-combinator-space-after': 'always',
    'selector-combinator-space-before': 'always',
    'selector-no-id': true,
    'selector-no-type': true,
    'selector-no-universal': true,
    'selector-no-vendor-prefix': true,
    'selector-pseudo-element-colon-notation': 'double',

    // Selector list
    'selector-list-comma-space-after': 'always-single-line',
    'selector-list-comma-space-before': 'never',

    // Media
    'media-feature-colon-space-after': 'always',
    'media-feature-colon-space-before': 'never',
    'media-feature-name-no-vendor-prefix': true,
    'media-feature-range-operator-space-after': 'always',
    'media-feature-range-operator-space-before': 'always',

    // Custom media
    'custom-media-pattern': 'xs|sm|md|lg|xlg|xxlg.+/',

    // Media query
    'media-query-parentheses-space-inside': 'never',

    // Comment
    'comment-whitespace-inside': 'always',

    // General
    'indentation': 2,
    'no-eol-whitespace': true,
    'no-missing-eof-newline': true,

    // Rules
    'rule-nested-empty-line-before': ['always', {
      except: ['first-nested'],
      ignore: ['after-comment']
    }],
    'rule-non-nested-empty-line-before': ['always-multi-line', {
      ignore: ['after-comment']
    }],
    'declaration-block-trailing-semicolon': 'always',
  }
}
