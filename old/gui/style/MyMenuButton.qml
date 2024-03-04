
import QtQuick 2.15
import QtQuick.Controls 2.15


Button {
    property var colorVariable // Объявление свойства для передачи переменной

    // Свойство для установки иконки
    property string iconSource: ""
    property string textSource: ""
    property string textOpacitySource: "0.0"

    // id:  menuCustomButton

    checkable: true
    ButtonGroup.group: group
    width: parent.width
    height: 30

    //anchors.left: parent.left
    background: Item {
        width:  parent.width
        height:  parent.height
        Rectangle {
            width:  parent.width - 4
            height:  parent.height
            color: checked ? "#43465a" : sideMenu.color
            anchors.right: parent.right
            anchors.rightMargin: -3
        }
        Rectangle {
            width:  parent.width
            height:  parent.height
            color: checked ? "#43465a" : colorVariable
            radius: 4  // Радиус закругления углов
        }
    }
    flat: true

    Behavior on width { NumberAnimation { duration: 500 } }

    anchors.leftMargin: 3
    // Текст
    Text {
        text: textSource
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        visible:  parent.width >= 120
        color: "#57a1eb"
        Behavior on opacity {
            NumberAnimation {
                duration: 500; // продолжительность анимации - 500 миллисекунд
            }
        }
        opacity: textOpacitySource
    }
    Image {
        id: icon_conf
        source: parent.iconSource
        anchors.left: parent.left
        anchors.verticalCenter: parent.verticalCenter
        anchors.leftMargin: 10
        width: 20
        height: 20
    }
    onClicked: {
        colorVariable = checked ? "#43465a" : sideMenu.color
    }
    onCheckedChanged: {
        if (!checked) {
            colorVariable = sideMenu.color
        }
    }


    // MouseArea для обработки событий наведения
    MouseArea {
        anchors.fill: parent // Заполняем всю область кнопки
        hoverEnabled: true   // Включаем обработку событий наведения
        propagateComposedEvents: true // Добавьте эту строку

        onEntered: {if (checked === false) {colorVariable = "#323544"} else {colorVariable = "#43465a"}} // Меняем цвет при наведении

        onExited: {if (checked === false) {colorVariable = sideMenu.color}} // Цвет кнопки совпадает с цветом sideMenu  // Возвращаем исходный цвет при уходе курсора
        onPressed: function(mouse) {
            mouse.accepted = false  // Это позволяет событию продолжить путешествие к Button
        }


    }

}
