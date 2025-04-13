'''Yksinkertainen GUI tulosten hallinnointiin
'''
# Komentokehotteen CTRL+C tappaa prosessin
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

STYLESHEET_NORMAL = "background-color: #31363b; color: white;"
STYLESHEET_ERROR = "background-color: #ff6a9a; color: black;"
STYLESHEET_OK = "background-color: #caecb0; color: black;"
STYLESHEET_NA = "background-color: #31363b; color: gray;"
STYLESHEET_TOOLTIP = '''QLineEdit {
    background-color: #31363b;
    color: white;
    }
    QToolTip {
    background-color: #31363b;
    color: white;
    }
'''
STYLESHEET_TABLEHEADER = '''QTableWidget {
    background-color: #31363b;
    color: white;
    }
    QHeaderView::section {
    background-color: #31363b;
    color: white;
    }
    QTableCornerButton::section {
    background-color: #31363b;
    color: white;
    }
'''
