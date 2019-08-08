import {createCustomElement} from './helpers/create-custom-element.js';

fetch('./static/templates/property-line.html')
  .then(stream => stream.text())
  .then(htmlContent => {
    let contentNode =
      document.createRange().createContextualFragment(htmlContent);
    createCustomElement('property-line', contentNode);
  });
