class Trello {
    constructor() {
    }

    start() {
        this.update();
    }

    update() {
        $.get();
        $("#trello");
    }
}

trello = new Trello();

$(function () {
    trello.start();
});
