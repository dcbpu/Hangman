import React, { Component } from 'react';
import { GlobalStyle } from './fonts';
import { SignInScreen, PlayScreen, WinScreen, LoseScreen } from './screens';
import axios from 'axios';

const APIURL = 'http://localhost:5000/';

class App extends Component {
    constructor(props) {
        super(props);
        this.state = {
            gameStatus: 'logged out'
        };
        this.startGame = this.startGame.bind(this);
        this.guessLetter = this.guessLetter.bind(this);
        this.playAgain = this.playAgain.bind(this);
        this.quitGame = this.quitGame.bind(this);
    };
    
    startGame(nameValue, passwordValue, registerNewAccount, langValue) {
    console.log(nameValue, passwordValue, registerNewAccount, langValue);

    // Step 1: Login or create account
    axios({
        method: registerNewAccount ? 'post' : 'put',
        url: APIURL + 'api/auth',
        data: { username: nameValue, password: passwordValue }
    })
        .then(response => {
        const { access_token } = response.data;

        // Update login-related state first
        this.setState(
            {
            username: nameValue,
            password: passwordValue,
            language: langValue,
            loginToken: access_token
            },
            () => {
            // Step 2: Create a new game, using the fresh loginToken
            axios({
                method: 'post',
                url: APIURL + 'api/games',
                data: { language: langValue },
                headers: { Authorization: 'Bearer ' + this.state.loginToken }
            })
                .then(response => {
                const { access_token, game_id } = response.data;
                console.log("New Game ID (from response):", game_id);

                // Step 3: Store the game token and game id
                this.setState(
                    {
                    gameId: game_id,
                    gameToken: access_token
                    },
                    () => {
                    console.log("Updated Game ID (from state):", this.state.gameId);

                    // Step 4: Fetch the initial game state
                    axios({
                        method: 'get',
                        url: APIURL + 'api/games/' + this.state.gameId,
                        headers: { Authorization: 'Bearer ' + this.state.loginToken }
                    })
                        .then(response => {
                        const {
                            bad_guesses,
                            guessed,
                            player,
                            reveal_word,
                            usage
                        } = response.data;

                        this.setState({
                            badGuesses: bad_guesses,
                            guessed: guessed,
                            playerId: player,
                            revealWord: reveal_word,
                            usage: usage,
                            gameStatus: 'active',
                            flashMessage: ''
                        });
                        })
                        .catch(() => {
                        this.setState({
                            flashMessage: 'Failed to access a new game',
                            gameToken: null
                        });
                        });
                    }
                );
                })
                .catch(() => {
                this.setState({
                    flashMessage: 'Failed to start a new game',
                    gameToken: null
                });
                });
            }
        );
        })
        .catch(() => {
        this.setState({
            flashMessage:
            'Account ' + (registerNewAccount ? 'creation' : 'login') + ' failed',
            loginToken: null
        });
        });
}

  guessLetter(letter, numCalls=0) {
    axios({
        method: 'put',
        url: APIURL + 'api/games/' + this.state.gameId,
        data: {letter},
        headers: {Authorization: 'Bearer ' + this.state.gameToken}
    }).then( response => {
        const { bad_guesses, guessed, reveal_word, result, secret_word } =
              response.data;            
        this.setState({
            badGuesses: bad_guesses,
            guessed: guessed,
            revealWord: reveal_word,
            gameStatus: result,
            secretWord: secret_word,
            flashMessage: ''
        });
    }).catch( error => {
        // Was it an expired token?
        if (error.response && (error.response.status === 400)) {
            if (error.response.data.msg === 'User claims verification failed') {
                if (numCalls === 4) {
                    this.setState({ flashMessage: 'Server not accepting credentials' });
                } else {
                    // try logging in again
                    axios({
                        method: 'put',
                        url: APIURL + 'api/auth',
                        data: { username: this.state.username,
                                password: this.state.password }
                    }).then( response => {
                        // with successful login, update the login token
                        this.setState({ loginToken: response.data.access_token });
                        axios({
                            method: 'get',
                            url: APIURL + 'api/games/' + this.state.gameId,
                            headers: {Authorization: 'Bearer ' + this.state.loginToken}
                        }).then( response => {
                            // on success, update the access token
                            this.setState({ gameToken: response.data.access_token }); 
                        });
                    }).finally( () => {
                        // and now try again, with a possibly corrected token
                        this.guessLetter(letter, numCalls+1);
                    });
                }
            }
        } else {
            // all other errors
            this.setState({ flashMessage: 'Server did not receive your guess' });
        }
    });
}

playAgain(langValue) {
    this.startGame(this.state.username, this.state.password, false, langValue);            
}
quitGame() {
    this.setState({gameStatus: 'logged out'});
}

      
    render() {
        const { gameStatus } = this.state;
        let screen = <></>;
        if (gameStatus === 'logged out') {
            const startGame = this.startGame;
            screen = (
                <SignInScreen
                    clickStart={startGame}
                    flashMessage={this.state.flashMessage}
                />
            );        
        } else if (gameStatus === 'active') {
            const { usage, revealWord, guessed, badGuesses,flashMessage } = this.state;
            const guessLetter = this.guessLetter;
            screen = <PlayScreen
                    usage = {usage}
                    blanks = {revealWord}
                    usedLetters = {guessed}
                    numBadGuesses = {badGuesses}
                    onGuess = {guessLetter}
                    flashMessage={flashMessage}
           />; }
           else if (gameStatus === 'won') {
                const { language } = this.state;
                const playAgain = this.playAgain;
                const quitGame = this.quitGame;
                screen = <WinScreen
                        lang={language}
                        clickPlayAgain={playAgain}
                        clickQuit={quitGame}
                      />;
          } else if (gameStatus === 'lost') {
              const { usage, secretWord, language } = this.state;
              const playAgain = this.playAgain;
              const quitGame = this.quitGame;
              screen = <LoseScreen
                      usage = {usage}
                      blanks = {secretWord}
                      lang = {language}
                      clickPlayAgain = {playAgain}
                      clickQuit = {quitGame}
                    />;
          } 
          else {
            screen = <div>Unexpected {gameStatus} </div>;
          }
        return <><GlobalStyle/>{screen}</>;
    }
}

export default App;
