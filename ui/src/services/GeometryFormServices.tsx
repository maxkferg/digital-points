export default class GeometrySingleton {
    private static instance: GeometrySingleton;
    private constructor () {
        GeometrySingleton.instance = {
            "walls": {
              id: "walls-",
              name: "walls-",
              type: "wall",
              filetype: "obj",
              filename: "walls.obj",
              directory: "/geometry/env/labv2/",
              scale: 1.0,
            },
            "floors": {
              id: "floor-",
              name: "floor-",
              type: "floor",
              filetype: "obj",
              filename: "floors.obj",
              directory: "/geometry/env/labv2/",
              scale: 1.0,
            },
            "robot": {
              id: "robot-",
              name: "robot-",
              type: "robot",
              filetype: "obj",
              filename: "turtlebot.obj",
              directory: "/geometry/robots/turtlebot2/",
              scale: 0.001,
            },
            "baseball": {
              id: "baseball-",
              name: "baseball-",
              type: "object",
              filetype: "obj",
              filename: "baseball.obj",
              directory: "/geometry/objects/baseball/",
              scale: 0.001,
            },
            "box": {
              id: "box-",
              name: "box-",
              type: "object",
              filetype: "obj",
              filename: "box.obj",
              directory: "/geometry/objects/box/",
              scale: 0.001,
            },
            "bucket": {
              id: "bucket-",
              name: "bucket-",
              type: "object",
              filetype: "obj",
              filename: "bucket.obj",
              directory: "/geometry/objects/bucket/",
              scale: 0.001,
            },
            "cycle": {
              id: "cycle-",
              name: "cycle-",
              type: "object",
              filetype: "obj",
              filename: "cycle.obj",
              directory: "/geometry/objects/cycle/",
              scale: 0.001,
            },
            "chair": {
              id: "chair-",
              name: "chair-",
              type: "object",
              filetype: "obj",
              filename: "chair.obj",
              directory: "/geometry/objects/chair/",
              scale: 0.03,
            },
            "gas can": {
              id: "gas-can-",
              name: "gas-can-",
              type: "object",
              filetype: "obj",
              filename: "gas-can.obj",
              directory: "/geometry/objects/gas-can/",
              scale: 0.1,
            },
            "gloves": {
              id: "glove-",
              name: "glove-",
              type: "object",
              filetype: "obj",
              filename: "glove.obj",
              directory: "/geometry/objects/gloves/",
              scale: 0.01,
            },
            "hard hat": {
              id: "hard-hat-",
              name: "hard-hat-",
              type: "object",
              filetype: "obj",
              filename: "hard-hat.obj",
              directory: "/geometry/objects/hard-hat/",
              scale: 0.001,
            },
            "recycle bin": {
              id: "recycle-bin-",
              name: "recycle-bin-",
              type: "object",
              filetype: "obj",
              filename: "recycle bin.obj",
              directory: "/geometry/objects/recycle-bin/",
              scale: 0.001,
            }
        };
    } 
    public static getInstance() : GeometrySingleton {
        if (!GeometrySingleton.instance) {
            return new GeometrySingleton();
        } else {
            return GeometrySingleton.instance;
        }
    }
}
