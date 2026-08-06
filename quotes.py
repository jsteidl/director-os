import random

QUOTES = [
    "The Answer to the Great Question of Life, the Universe and Everything is 42.",
    "Time is an illusion. Lunchtime doubly so.",
    "Don't Panic.",
    "I may not have gone where I intended to go, but I think I have ended up where I needed to be.",
    "The ships hung in the sky in much the same way that bricks don't.",
    "Anyone who is capable of getting themselves made President should on no account be allowed to do the job.",
    "A common mistake that people make when trying to design something completely foolproof is to underestimate the ingenuity of complete fools.",
    "We demand rigidly defined areas of doubt and uncertainty.",
    "The major difference between a thing that might go wrong and a thing that cannot possibly go wrong is that when a thing that cannot possibly go wrong goes wrong it usually turns out to be impossible to get at or repair.",
    "Nothing travels faster than the speed of light, with the possible exception of bad news.",
    "In the beginning the Universe was created. This has made a lot of people very angry and been widely regarded as a bad move.",
    "For a moment, nothing happened. Then, after a second or so, nothing continued to happen.",
    "The knack of flying is learning how to throw yourself at the ground and miss.",
    "He felt that his whole life was some kind of dream and he sometimes wondered whose it was and whether they were enjoying it.",
    "Reality is frequently inaccurate.",
    "I'd far rather be happy than right any day.",
    "There is a theory which states that if ever anyone discovers exactly what the Universe is for and why it is here, it will instantly disappear and be replaced by something even more bizarre and inexplicable.",
    "The world is a thing of utter inordinate complexity and richness and strangeness that is absolutely awesome.",
    "We are stuck with technology when what we really want is just stuff that works.",
    "A learning experience is one of those things that says, 'You know that thing you just did? Don't do that.'",
    "The impossible often has a kind of integrity to it which the merely improbable lacks.",
    "If it looks like a duck, and quacks like a duck, we have at least to consider the possibility that we have a small aquatic bird of the family Anatidae on our hands.",
    "Human beings, who are almost unique in having the ability to learn from the experience of others, are also remarkable for their apparent disinclination to do so.",
    "All opinions are not equal. Some are a very great deal more robust, sophisticated and well supported in logic and argument than others.",
    "I love deadlines. I love the whooshing noise they make as they go by.",
    "You live and learn. At any rate, you live.",
    "The art of flying lies in learning how to throw yourself at the ground and miss.",
    "It is a mistake to think you can solve any major problems just with potatoes.",
    "Space is big. Really big. You just won't believe how vastly, hugely, mind-bogglingly big it is.",
    "Would it save you a lot of time if I just gave up and went mad now?",
]


def get_random_quote():
    return random.choice(QUOTES)
