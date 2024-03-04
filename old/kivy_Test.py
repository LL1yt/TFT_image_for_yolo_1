from kivymd.app import MDApp
from kivymd.uix.list import OneLineIconListItem, MDList
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.icon_definitions import md_icons
from kivy.uix.scrollview import ScrollView


class ContentNavigationDrawer(MDBoxLayout):
    pass


class ItemDrawer(OneLineIconListItem):
    icon = "folder"


class DrawerList(ScrollView):
    def __init__(self, **kwargs):
        super(DrawerList, self).__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (300, 500)  # Установка размера ScrollView

        # Создание списка и добавление его в ScrollView
        self.list_view = MDList()
        self.add_widget(self.list_view)

        # Добавление элементов в список
        for i in range(20):
            self.list_view.add_widget(ItemDrawer(text=f"Item {i}"))


class MainApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "BlueGray"  # Опционально: установка темы
        return DrawerList()


if __name__ == "__main__":
    MainApp().run()
