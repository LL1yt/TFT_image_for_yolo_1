//import Felgo
import QtQuick 2.15
import QtQuick.Controls 2.15
import "style"
ApplicationWindow {
    id: main
    visible: true
    width: 1440
    height: 900
    title: "TftProject"
    color: "#43465a"

    // Состояние для контроля разворачивания/сворачивания меню
    property bool isMenuVisible: false

    // Свойство для отслеживания состояния кнопки
    property bool buttonState: false

    // Свойство для отслеживания состояния кнопки
    property bool buttonMenuConfigState: false
    property bool buttonMenuSelectState: false
    property string currentPage : "configPage"

    // Стек для управления страницами
    Loader {
        id: configPage
        height: parent.height
        anchors.right: parent.right
        width: parent.width - sideMenu.width
        source: Qt.resolvedUrl("style/Configuration.qml")
        visible: main.currentPage === "configPage"
    }
    Loader {
        id: settingsPage
        height: parent.height
        anchors.right: parent.right
        width: parent.width - sideMenu.width
        source: Qt.resolvedUrl("style/Settings.qml")
        visible: main.currentPage === "settingsPage"
    }

    Rectangle {
        id: sideMenu
        width: isMenuVisible ? 250 : 50 // 20 пикселей видны, когда меню свернуто
        height: parent.height
        color: "#272833"

        // Свойство для хранения текущего цвета кнопки
        property color buttonColor: "#272833" // Начальный цвет кнопки

        // Свойство для хранения текущего цвета кнопки
        property color buttonMenuConfigColor: "#272833" // Начальный цвет кнопки

        // Свойство для хранения текущего цвета кнопки
        property color buttonMenuSettingsColor: "#272833" // Начальный цвет кнопки

        Behavior on width {
            PropertyAnimation { duration: 500 }
        }

        // Свойство для хранения текущего цвета кнопки
        // Начальный цвет кнопки

        Button {


            id:  menuExpandButton
            width: 44
            height: 30
            anchors.left: parent.left
            anchors.top: parent.top
            background: Rectangle {
                color: sideMenu.buttonColor
                radius: 4  // Радиус закругления углов
            } // Используем buttonColor для фона кнопки 57a1eb
            flat: true

            Behavior on width { NumberAnimation { duration: 500 } }

            anchors.topMargin: 3
            anchors.leftMargin: 3
            Image {
                id: icon_back
                source: "style/images/icons/icons8_back_50.png"
                anchors.left: parent.left
                anchors.verticalCenter: parent.verticalCenter
                opacity: 0.0
                anchors.leftMargin: 10
                width: 20
                height: 20
                visible:  menuExpandButton.width >= 190  // Видимость зависит от isPressed
                Behavior on opacity {
                    NumberAnimation {
                        duration: 500; // продолжительность анимации - 500 миллисекунд
                    }
                }
            }
            // Текст
            Text {
                id: text_Expand_menu
                text: "Hide Menu"
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter
                opacity: 0.0
                visible:  menuExpandButton.width >= 60
                color: "#57a1eb"
                Behavior on opacity {
                    NumberAnimation {
                        duration: 500; // продолжительность анимации - 500 миллисекунд
                    }
                }
            }
            Image {
                id: icon_menu
                source: "style/images/icons/icons8_menu_50_bl.png"
                anchors.left: parent.left
                anchors.verticalCenter: parent.verticalCenter
                opacity: 1.0
                anchors.leftMargin: 10
                width: 20
                height: 20
                //visible:  menuExpandButton.width <= 190  // Видимость зависит от isPressed
                Behavior on opacity {
                    NumberAnimation {
                        duration: 500; // продолжительность анимации - 500 миллисекунд
                    }
                }
            }

            onClicked: {

                isMenuVisible = !isMenuVisible
                // Переключение состояния кнопки
                buttonState = !buttonState


                menuExpandButton.width =  menuExpandButton.width === 44 ? 244 : 44
                icon_menu.opacity = icon_menu.opacity === 1.0 ? 0.0 : 1.0
                icon_back.opacity = icon_back.opacity === 1.0 ? 0.0 : 1.0
                text_Expand_menu.opacity = text_Expand_menu.opacity === 1.0 ? 0.0 : 1.0
                columnForMenuButtons.width =  columnForMenuButtons.width === 44 ? 244 : 44


                sideMenu.buttonColor = buttonState ? "#323343" : sideMenu.color

            }

            // MouseArea для обработки событий наведения
            MouseArea {
                anchors.fill: parent // Заполняем всю область кнопки
                hoverEnabled: true   // Включаем обработку событий наведения
                propagateComposedEvents: true // Добавьте эту строку

                onEntered: {sideMenu.buttonColor = "#323544"} // Меняем цвет при наведении

                onExited: {if (buttonState === false) {sideMenu.buttonColor = sideMenu.color} else {sideMenu.buttonColor = "#44475a"}} // Цвет кнопки совпадает с цветом sideMenu  // Возвращаем исходный цвет при уходе курсора
                onPressed: function(mouse){
                    mouse.accepted = false  // Это позволяет событию продолжить путешествие к Button
                }



            }

        }
        // Цветная линия под кнопкой
        Rectangle {

            id: lineS
            width:  menuExpandButton.width
            height: 4  // Высота линии

            anchors.left: parent.left
            color: "#323544"  // Цвет линии
            anchors.top:  menuExpandButton.bottom
            anchors.horizontalCenter:  menuExpandButton.horizontalCenter
            anchors.topMargin: 3
            //anchors.leftMargin: 3

        }

        ButtonGroup { id: group }

        Column {
            id: columnForMenuButtons
            width: 44
            spacing: 3
            anchors.topMargin: 3

            anchors.leftMargin: 3
            anchors.left: parent.left
            anchors.top:  lineS.bottom

            MyMenuButton {
                id: menuConfigButton
                textSource: "Configuration"
                iconSource: "images/icons/icons8_conf_50.png"
                colorVariable: sideMenu.buttonMenuConfigColor
                textOpacitySource: text_Expand_menu.opacity
                checked: true // эту кнопку выделить по умолчанию
                Binding { // Создание связывания
                    target: sideMenu
                    property: "buttonMenuConfigColor"
                    value: menuConfigButton.colorVariable
                }
                onClicked: {
                    main.currentPage = "configPage"
                }
            }

            MyMenuButton {
                id: menuSettingsButton
                textSource: "Settings"
                iconSource: "images/icons/icons8_settings_50.png"
                colorVariable: sideMenu.buttonMenuSettingsColor
                textOpacitySource: text_Expand_menu.opacity
                Binding { // Создание связывания
                    target: sideMenu
                    property: "buttonMenuSettingsColor"
                    value: menuConfigButton.colorVariable
                }
                onClicked: {
                    main.currentPage = "settingsPage"
                }
            }

            // Добавьте здесь дополнительные кнопки...
        }

    }
}
