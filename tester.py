from pesapal_v3 import Pesapal


def main():
    key = "qkio1BGGYAXTu2JOfm7XSXNruoZsrqEW"
    secret = "osGQ364R49cXKeOYSpaOnT++rHs="
    client = Pesapal(consumer_key=key, consumer_secret=secret)
    if client._token:
        ipn_url = "https://example.com/ipn/notifications"
        ipn = client.register_ipn_url(ipn_url=ipn_url)
        if ipn.status != "200":
            print(ipn.error)
        print(ipn)


if __name__ == "__main__":
    main()
