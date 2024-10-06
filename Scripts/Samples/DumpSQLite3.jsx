function DumpSQLite3() {
    var dbPath = File.saveDialog("Save SQLite3 Database", "*.db");
    if (dbPath == null) {
        return;
    }

    var sqlite3 = Python.import("sqlite3");
    var con = sqlite3.callattr("connect", [dbPath.fsName]);
    var cur = con.callattr("cursor");

    cur.callattr("execute", ["CREATE TABLE comps(id, name)"]);
    cur.callattr("execute", ["CREATE TABLE layers(comp_id, name)"]);

    var comps = [];
    for (var i = 1; i <= app.project.numItems; i++) {
        var item = app.project.item(i);
        if (item instanceof CompItem) {
            comps.push(item);
        }
    }

    for (var i = 0; i < comps.length; i++) {
        var comp = comps[i];
        cur.callattr("execute", ["INSERT INTO comps VALUES(?, ?)", [i, comp.name]]);

        var layers = [];
        for (var j = 1; j <= comp.numLayers; j++) {
            var layer = comp.layer(j);
            layers.push([i, layer.name]);
        }

        cur.callattr("executemany", ["INSERT INTO layers VALUES(?, ?)", layers]);
    }

    con.callattr("commit");
    con.callattr("close");
}

DumpSQLite3();
