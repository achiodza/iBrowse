import sys
import requests
from io import BytesIO
from PIL import ImageTk, Image
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTabWidget, QTextBrowser, QLabel, QMessageBox
from PyQt5.QtGui import QIcon, QPixmap, QFontDatabase
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings


class BrowserTab(QWidget):
    def __init__(self):
        super().__init__()

        # Create a layout for the tab
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create a web browser widget
        self.webview = QWebEngineView()
        self.webview.page().profile().downloadRequested.connect(self.handle_download)
        self.webview.setOpenLinks(False)  # Disable opening links in external browser
        layout.addWidget(self.webview)

        # Create a layout for the toolbar
        toolbar_layout = QHBoxLayout()
        layout.addLayout(toolbar_layout)

        # Create the navigation buttons
        back_button = QPushButton("Back")
        back_button.clicked.connect(self.go_back)
        toolbar_layout.addWidget(back_button)

        forward_button = QPushButton("Forward")
        forward_button.clicked.connect(self.go_forward)
        toolbar_layout.addWidget(forward_button)

        home_button = QPushButton("Home")
        home_button.clicked.connect(self.go_home)
        toolbar_layout.addWidget(home_button)

        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh)
        toolbar_layout.addWidget(refresh_button)

        # Create an input field for the URL
        self.url_input = QLineEdit()
        self.url_input.returnPressed.connect(self.open_url)
        toolbar_layout.addWidget(self.url_input)

        # Create a loading indicator
        self.loading_label = QLabel()
        layout.addWidget(self.loading_label, alignment=Qt.AlignBottom)

        # Create an empty favicon image
        self.favicon_img = QPixmap(16, 16)

    def go_back(self):
        self.webview.back()

    def go_forward(self):
        self.webview.forward()

    def go_home(self):
        self.webview.setUrl(QUrl(""))

    def refresh(self):
        self.webview.reload()

    def open_url(self):
        url = self.url_input.text()
        if url.startswith("http://") or url.startswith("https://"):
            self.update_browser(url)
        else:
            QMessageBox.warning(self, "Invalid URL", "Please enter a valid URL starting with 'http://' or 'https://'")

    def block_ads(self, url):
        if self.ad_block_enabled.get():
            # Implement your ad-blocking logic here
            if "ads" in url:
                return True
        return False

    def update_browser(self, url):
        self.loading_label.setText("Loading...")
        self.loading_label.repaint()

        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, "html.parser")
            self.webview.setHtml(str(soup))
            self.update_favicon(url)
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

        self.loading_label.setText("")

    def update_favicon(self, url):
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, "html.parser")
            favicon_link = soup.find("link", rel="icon")
            if favicon_link:
                favicon_url = favicon_link["href"]
                if not favicon_url.startswith("http"):
                    favicon_url = url + favicon_url
                favicon_response = requests.get(favicon_url)
                favicon_data = favicon_response.content
                favicon_image = Image.open(BytesIO(favicon_data))
                favicon_image = favicon_image.resize((16, 16), Image.ANTIALIAS)
                self.favicon_img = QPixmap.fromImage(ImageTk.ImageQt(favicon_image))

        except Exception as e:
            print("Error updating favicon:", str(e))


class WebBrowser(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create the main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Create a layout for the main widget
        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        # Create a tab widget for managing browser tabs
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # Create the initial tab
        self.new_tab()

    def new_tab(self):
        tab = BrowserTab()
        self.tab_widget.addTab(tab, "New Tab")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Enable OpenType font support
    settings = QWebEngineSettings.globalSettings()
    settings.setFontFamily(QWebEngineSettings.StandardFont, "Font Name")

    browser = WebBrowser()
    browser.show()

    sys.exit(app.exec_())
