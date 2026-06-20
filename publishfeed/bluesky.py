from atproto import Client

class Bluesky:

    def __init__(self, handle, password):
        self.handle = handle
        self.password = password
        self.client = Client()

    def update_status(self, text):
        """
        Post a message to Bluesky.
        text can be a string or an atproto client_utils.TextBuilder object.
        """
        try:
            print(f"Logging in to Bluesky as {self.handle}...")
            self.client.login(self.handle, self.password)
            print("Posting to Bluesky...")
            response = self.client.send_post(text)
            print(f"Bluesky post success. URI: {response.uri}")
            return response
        except Exception as e:
            print(f"Error posting to Bluesky: {e}")
            raise e
