import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    anchors.fill: parent
    anchors.right: parent.right
    // Содержимое страницы конфигурации
    Rectangle {
        anchors.fill: parent
        color: main.color
        Label {
            text: "Страница Конфигурации"
            anchors.centerIn: parent
        }
    }
}
