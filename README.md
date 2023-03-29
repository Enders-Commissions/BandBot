# BandBot
This is another bot I've made for a customer. I named it "Band Bot", because I think it could be useful for bands planning what day band members will play.
Using the `config.py` you can set a time, at that time, a message is sent if the current day is the one you set in the `config.py` file.
The message is basically a list of all days, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, and the message has 6 reactions.
The reactions are basically just numbers from 1 to 6. Reacting with 1, will add you to Monday, unreacting with 1 will remove you from it.
You can also join as many days as you want to. Note that this does require a database, which you can setup in `config.py`.