// .storybook/preview.js
import React from 'react';
import { GlobalStyle } from '../src/fonts';

export const decorators = [
  (Story) => (
    <>
      <GlobalStyle />
      <Story />
    </>
  ),
];

export const parameters = {
  actions: { argTypesRegex: "^on[A-Z].*" },
};