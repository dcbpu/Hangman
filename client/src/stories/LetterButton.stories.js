import React from 'react';
import { LetterButton } from '../buttons';

export default {
  title: 'Button-related Components/LetterButton',
  component: LetterButton,
};

// Helper function to log clicks
const logClick = (name) => (...args) => {
  console.log(`${name} clicked`, ...args);
};

// --- Stories ---
export const AlreadyUsed = {
  render: () => (
    <LetterButton letter="A" wasUsed={true} makeGuess={logClick('click-A')} />
  ),
};

export const NotYetUsed = {
  render: () => (
    <LetterButton letter="B" wasUsed={false} makeGuess={logClick('click-B')} />
  ),
};


