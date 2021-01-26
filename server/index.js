var http = require('http');
var fs = require("fs");
var WebSocketServer = require('ws').Server;
// const uuid = require('uuid');

var wsPort = 5000;
var users = {};
var httpServer = http.createServer({}).listen(wsPort);
var wss = new WebSocketServer({ server: httpServer });
wss.on('connection', function (ws) {

    ws.on('message', function (message) {
        try {
            type = message.toString("utf8", 0, 10).trim()
            switch (type) {
                case "connection":
                    name = message.toString("utf8", 10, 20).trim()
                    broadcaster = message.slice(20, 21).readUInt8()
                    speaker = message.slice(21, 22).readUInt8()
                    ws.name = name
                    users[name] = { name: name, broadcaster: Boolean(broadcaster), speaker: Boolean(speaker), ws: ws }
                    console.log("Connection opened: " + ws.name)
                    break;
                case "ping":
                    users[ws.name].ws.send(message)
                    break;
                default:
                    for (var name in users) {
                        // if(user.name != ws.name && user.speaker){
                        if (users[name].speaker) {
                            users[name].ws.send(message)
                        }
                    }
                    break;
            }
        } catch (e) {
            console.log(e)
            console.log("Error on: " + message.toString())
        }
    });

    ws.on('close', function () {
        console.log("Connection closed: " + ws.name)
    });

});


