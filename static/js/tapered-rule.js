import {createCustomElement} from './helpers/create-custom-element.js';

fetch('./static/templates/tapered-rule.html')
  .then(stream => stream.text())
  .then(htmlContent => {
    let contentNode =
      document.createRange().createContextualFragment(htmlContent);
    createCustomElement('tapered-rule', contentNode);
  });
