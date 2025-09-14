Langman documentation
=====================

Flask Server API
----------------

.. automodule:: server.api
   :members:

Database ORM and Schema
-----------------------

.. automodule:: server.langman_orm
   :members:

Client Stylesheet
-----------------

`Storybook Stylesheet <_static/storybook-static/index.html>`_
(Requires JavaScript)


Client Application
------------------
The following describes the JavaScript client.

.. js:module:: App

.. js:class:: App

   .. js:method:: constructor(props)

      The React lifecycle method to initialize the component.  Sets
      the state ``gameStatus`` to 'logged out'.  Also, binds methods.

      :param props object: The collection of properties for the
                           object, which are typically set using JSX
                           within a render method, but for this top
                           level component come directly from React.

   .. js:method:: startGame(nameValue, langValue)

      Contacts server to start a new game, then updates state accordingly.

      :param nameValue string: Name of player
      :param langValue string: Two-letter string indicating language choice

      State is set for ``username``, ``language``, ``gameId``,
      ``badGuesses``, ``guessed``, ``playerId``, ``revealWord``,
