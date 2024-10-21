from webbrowser import open as open_browser


def url(url: str):
    open_browser(url)
    return f"opened {url.split('.')[1]} website."


if __name__ == "__main__":
    r = url("https://www.dominos.com/")
    print(r)