import random
from flask import Blueprint, jsonify, request

facts_bp = Blueprint("facts", __name__)

FACTS = [
    "A dog's nose print is as unique as a human fingerprint — no two are alike.",
    "Cats have a specialized collarbone that lets them always land on their feet after a fall.",
    "A group of cats is called a clowder, and a group of kittens is called a kindle.",
    "Dogs can smell about 100,000 times better than humans, thanks to up to 300 million olfactory receptors.",
    "Cats spend roughly 70% of their lives asleep — about 13–16 hours a day.",
    "A dog's sense of smell is so powerful it can detect some cancers and low blood sugar levels.",
    "Rabbits can see nearly 360 degrees around them, but have a blind spot right in front of their nose.",
    "A cat's purr vibrates at 25–150 Hz, a frequency known to promote bone healing and reduce stress.",
    "Dogs have three eyelids — the third, called the nictitating membrane, helps protect and moisten the eye.",
    "Parrots can live longer than 80 years, making them one of the longest-lived pet species.",
    "A cat's heart beats almost twice as fast as a human heart: 140–220 beats per minute.",
    "Goldfish can live for over 20 years with proper care — the oldest on record lived to 43.",
    "Dogs sweat primarily through the pads of their feet, not through their skin.",
    "A guinea pig's teeth never stop growing — they need fibrous food to keep them worn down naturally.",
    "Cats have 32 muscles in each ear, allowing them to rotate their ears 180 degrees.",
    "Hamsters can run up to 5 miles in a single night on their wheel.",
    "A dog's normal body temperature is 101–102.5°F — higher than a human's 98.6°F.",
    "Birds have hollow bones, which reduce their weight and make flight possible.",
    "A cat can jump up to six times its own body length in a single leap.",
    "Ferrets sleep 14–18 hours a day and can enter a deep sleep so soundly they're difficult to wake.",
    "Turtles can breathe through their butts — they absorb oxygen through their cloaca in winter.",
    "A dog's mouth contains fewer bacteria than a human mouth, though both still need regular dental care.",
    "Senior dogs (7+) benefit from twice-yearly vet visits to catch age-related conditions early.",
    "Cats are obligate carnivores — they require nutrients found only in animal tissue to survive.",
    "Regular dental cleanings can extend a pet's life by reducing heart, kidney, and liver disease risk.",
]

_last_fact = None


@facts_bp.route("/", methods=["GET"])
def get_fact():
    global _last_fact
    choices = [f for f in FACTS if f != _last_fact]
    fact = random.choice(choices)
    _last_fact = fact
    return jsonify({"fact": fact}), 200
