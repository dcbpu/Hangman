import React from 'react';
import { LetterButton, ButtonPanel, StartForm, PlayAgainPanel } from '../buttons';
import { Banner, ResultBanner, UsageAndBlanks } from '../components';
import { Gallows } from '../gallows';
import { SignInScreen, WinScreen, LoseScreen, PlayScreen } from '../screens';

export default {
  title: 'Button-related Components',
};

// Helper function to log clicks
const logClick = (name) => (...args) => {
  console.log(`${name} clicked`, ...args);
};

// --- LetterButton ---
export const LetterButtonAlreadyUsed = {
  name: 'LetterButton - Already Used',
  render: () => (
    <LetterButton letter="A" wasUsed={true} makeGuess={logClick('click-A')} />
  ),
};

export const LetterButtonNotYetUsed = {
  name: 'LetterButton - Not Yet Used',
  render: () => (
    <LetterButton letter="B" wasUsed={false} makeGuess={(e) => console.log('click-B', e)} />
  ),
};


// --- ButtonPanel ---
export const ButtonPanelStory = {
  name: 'ButtonPanel Examples',
  render: () => (
    <div>
      <h2>ButtonPanel(language, onGuess)</h2>
      <ul>
        <li><b>onGuess</b> - a callback that takes the guessed letter</li>
        <li><b>usedLetters</b> - string of already-guessed letters</li>
      </ul>

      <h3>Used Letters: rlstine</h3>
      <ButtonPanel onGuess={(letter) => console.log('guessed', letter)} usedLetters="rlstine" />

      <h3>Used Letters: senorita</h3>
      <ButtonPanel onGuess={(letter) => console.log('guessed', letter)} usedLetters="senorita" />

      <h3>Used Letters: mondieu</h3>
      <ButtonPanel onGuess={(letter) => console.log('guessed', letter)} usedLetters="mondieu" />
    </div>
  ),
};

// --- StartForm ---
export const StartFormStory = () => (
  <div>
    <h2>StartForm(clickStart)</h2>
    <ul>
      <li>clickStart - game starting callback, takes name and language</li>
    </ul>
    <StartForm clickStart={(name, language) => console.log('start-game', { name, language })} />
  </div>
);


export const StartFormTest = {
  render: () => (
    <form>
      <input type="text" placeholder="Name" />
      <select>
        <option value="en">English</option>
        <option value="fr">French</option>
      </select>
      <button>Start Game</button>
    </form>
  ),
};


// --- PlayAgainPanel ---
export const PlayAgainPanelStory = {
  name: 'PlayAgainPanel Example',
  render: () => (
    <div>
      <h2>PlayAgainPanel(lang, clickPlayAgain)</h2>
      <ul>
        <li>lang - the language in which the last game was played</li>
        <li>clickPlayAgain - callback taking the new language choice</li>
        <li>clickQuit - callback to quit playing</li>
      </ul>

      <h3>Default English</h3>
      <PlayAgainPanel
        lang="en"
        clickPlayAgain={() => console.log('play again')}
        clickQuit={() => console.log('quit game')}
      />

      <h3>Default French</h3>
      <PlayAgainPanel
        lang="fr"
        clickPlayAgain={() => console.log('play again')}
        clickQuit={() => console.log('quit game')}
      />
    </div>
  ),
};

// --- Banners and Displays ---
export const BannerStory = {
  name: 'Banner Example',
  render: () => (
    <div>
      <h2>Banner(full)</h2>
      <p>
        This component includes both Banner and ShortTitle from the design docs.
      </p>
      <ul>
        <li>
          full - truthy means wide title is shown with subtitle, otherwise shows just short title
        </li>
      </ul>
      <h3>Full Title</h3>
      <Banner full={true} />
      <h3>Short Title</h3>
      <Banner full={false} />
    </div>
  ),
};

export const ResultBannerStory = {
  name: 'ResultBanner Example',
  render: () => (
    <div>
      <h2>Result Banner</h2>
      <ul>
        <li>winResult - truthy means the player won, otherwise the player lost</li>
      </ul>

      <h3>Player Won the Game</h3>
      <ResultBanner winResult={true} />

      <h3>Player Lost the Game</h3>
      <ResultBanner winResult={false} />
    </div>
  ),
};

// --- UsageAndBlanks ---
export const UsageAndBlanksStory = {
  name: 'UsageAndBlanks Example',
  render: () => (
    <div>
      <h2>UsageAndBlanks(usage, blanks, showBlanks)</h2>
      <p>This component uses the non-React function prepareUsage.</p>
      <ul>
        <li>usage - usage example with guess word as underscores</li>
        <li>blanks - guessed/non-guessed letters, like "h_ml_t"</li>
        <li>showBlanks - whether to show blanks separately or in usage</li>
      </ul>          

      <h3>With blanks</h3>
      <UsageAndBlanks
        usage="The sky loomed dark and ______."
        blanks="__oo_y"
        showBlanks={true}
      />

      <h3>Without blanks</h3>
      <UsageAndBlanks
        usage="The sky loomed dark and ."
        blanks="gloomy"
        showBlanks={true}
      />
    </div>
  ),
};

// --- Gallows ---
export const GallowsStory = {
  name: 'Gallows Example',
  render: () => (
    <div>
      <h2>Gallows(badGuesses)</h2>
      <ul>
        <li>badGuesses - number (0 to 6) of parts to draw</li>
      </ul>
      <h3>0 Wrong Guesses</h3>
      <Gallows badGuesses={0} />
      <h3>3 Wrong Guesses</h3>
      <Gallows badGuesses={3} />
      <h3>6 Wrong Guesses</h3>
      <Gallows badGuesses={6} />
    </div>
  ),
};

export const SignInScreenStory = {
  name: 'SignInScreen Example',
  render: () => (
    <div>
      <h2>SignInScreen(clickStart)</h2>
      <ul>
        <li>clickStart - game-starting callback; gets name, language</li>
      </ul>
      <SignInScreen clickStart={(name, lang) => console.log('start-game', { name, lang })} />
    </div>
  ),
};

export const WinScreenStory = {
  name: 'WinScreen Example',
  render: () => (
    <div>
      <h2>WinScreen(lang, clickPlayAgain, clickQuit)</h2>
      <ul>
        <li>lang - the language in which the last game was played</li>
        <li>clickPlayAgain - callback taking the new language choice</li>
        <li>clickQuit - callback to quit playing</li>
      </ul>
      <h3>Expecting English</h3>
      <WinScreen 
        lang="en" 
        clickPlayAgain={(lang) => console.log('play again', lang)}
        clickQuit={() => console.log('quit game')}
      />
      <h3>Expecting Spanish</h3>
      <WinScreen 
        lang="es" 
        clickPlayAgain={(lang) => console.log('play again', lang)}
        clickQuit={() => console.log('quit game')}
      />
    </div>
  ),
};


export const LoseScreenStory = {
  name: 'LoseScreen Example',
  render: () => (
    <div>
      <h2>LoseScreen(usage, blanks, lang, clickPlayAgain, clickQuit)</h2>
      <ul>
        <li>usage - the usage example from the game just ending</li>
        <li>blanks - the word to be guessed for the game just ending</li>
        <li>lang - the language in which the last game was played</li>
        <li>clickPlayAgain - callback taking the new language choice</li>
        <li>clickQuit - callback to quit playing</li>
      </ul>

      <h3>English Example</h3>
      <LoseScreen
        usage="Therefore, send not to know for whom the bell _____, it tolls for thee."
        blanks="tolls"
        lang="en"
        clickPlayAgain={(lang) => console.log('play again', lang)}
        clickQuit={() => console.log('quit game')}
      />

      <h3>Spanish Example</h3>
      <LoseScreen
        usage="Los _________ nunca abandonan y los que abandonan nunca ganan."
        blanks="ganadores"
        lang="es"
        clickPlayAgain={(lang) => console.log('play again', lang)}
        clickQuit={() => console.log('quit game')}
      />
    </div>
  ),
};

export const PlayScreenStory = {
  name: 'PlayScreen Example',
  render: () => (
    <div>
      <h2>PlayScreen(usage, blanks, usedLetters, numBadGuesses, onGuess)</h2>
      <ul>
        <li>usage - the usage example provided as a clue</li>
        <li>blanks - blanks and right guesses for the secret word</li>
        <li>usedLetters - a string of letters that have been guessed</li>
        <li>numBadGuesses - number of wrong guesses</li>
        <li>onGuess - callback to use when guessing a letter</li>
      </ul>

      <h3>Typical Game</h3>
      <PlayScreen
        usage="All happy families are alike; each unhappy ______ is unhappy in its own way."
        blanks="_a____"
        usedLetters="acr"
        numBadGuesses={2}
        onGuess={(letter) => console.log('guess', letter)}
      />
    </div>
  ),
};




