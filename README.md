## Euchre game environment
Euchre is a popular trick-taking card game played a lot in the midwest. I play it with family all the time. Euchre has a small (but still big) state space as far as card games go (24 cards, 4 players, 5 tricks per round).

How would a reinforcement learning agent do at learning this game? From experience, there is a general strategy to play the game (there is usually one correct play at any given time), but this consists of lots of rules depending on the situation. Assessing the odds of a winning hand can also be hard.

Let's get the game written first, and maybe put a front end on it.

This looks very pertinent: https://web.stanford.edu/class/aa228/reports/2020/final165.pdf

*The American Hoyle; or, Gentleman's hand-book of games* on Library of Congress, apparently considered the holy grail of Euchre strategy: [link](https://www.loc.gov/resource/dcmsiabooks.americanhoyleorg00dick_0/?sp=2&st=pdf&pdfPage=1). The guy named Hoyle predates the existence of Euchre though.

Someone made a JavaScript library to render cards (though it looks like it may not be maintained anymore): https://github.com/richardschneider/cardsJS
