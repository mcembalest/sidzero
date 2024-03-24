from modules import detect_input, respond, respond_with_calculate, respond_with_outfit_roast, respond_with_search

def test_detect_input():
    print("\n\n~~~~~~~~~~~~~~~~~~~~~~~~~~~\ntesting detect_input module")
    snippets = ["doorbell", "Hey robot whats up", "burger", "What food is that?"]
    chats = [[], [], [], ["user: give me some food recs", "robot: oh i havea  good suggestion food"]]
    for s, c in zip(snippets, chats):
        print('\n\n>>>>>', s, c)
        detection_generator = detect_input(s, c, debug=False)
        for chunk in detection_generator:
            print(chunk, end='', flush=True)
        print("\n\n***")


def test_respond():
    print("\n\n~~~~~~~~~~~~~~~~~~~~~~~~~~~\ntesting respond module")
    chats = [["user: Hey robot whats up"], ["user: give me some food recs", "robot: oh i have a good suggestion for food, but its really really spicy", "user: What food is that?"]]
    for c in chats:
        print('\n\n>>>>>', c)
        response_generator = respond(c, attitude = "mean, insulting", debug=False)
        for chunk in response_generator:
            print(chunk, end='', flush=True)
        print("\n\n***")


def test_respond_with_calculate():
    print("\n\n~~~~~~~~~~~~~~~~~~~~~~~~~~~\ntesting respond_with_calculate module")
    queries = ["how many 3s are in 2^16", 'how far is it from nyc to LA']
    for q in queries:
        print('\n\n>>>>>', q)
        response_generator = respond_with_calculate(q, debug=False)
        for chunk in response_generator:
            print(chunk, end='', flush=True)
        print("\n\n***")


def test_respond_with_outfit_roast():
    print("\n\n~~~~~~~~~~~~~~~~~~~~~~~~~~~\ntesting respond_with_outfit_roast module")
    image_files = ["img/test/kfc.jpg"]
    for img in image_files:
        print('\n\n>>>>>', img)
        response_generator = respond_with_outfit_roast(img, debug=False)
        for chunk in response_generator:
            print(chunk, end='', flush=True)
        print("\n\n***")


def test_search():
    print("\n\n~~~~~~~~~~~~~~~~~~~~~~~~~~~\ntesting search module")
    queries = ["what is the current status of nikki haley in the 2024 presidental election", "what did dune 2 get on rotten tomatoes", "when is half life 3 coming out"]
    for q in queries:
        print('\n\n>>>>>', q)
        response_generator = respond_with_search(q, debug=False)
        for chunk in response_generator:
            print(chunk, end='', flush=True)
        print("\n\n***")


if __name__=="__main__":
    test_respond_with_calculate()
