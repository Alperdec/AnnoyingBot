const functions = require("firebase-functions");
const admin = require("firebase-admin");
const express = require("express");
const cors = require("cors");


admin.initializeApp();
const db = admin.firestore();
// const db = admin.firestore();
const app = express();
app.use(cors({origin: true}));

// all users initialized with 1 point
app.post("/", async (req, res) => {
  const discordUser = {
    name: req.body["name"],
    points: (typeof req.body["points"] == "string") ?
    parseInt(req.body["points"], 10) :
    req.body["points"],
  };
  if (typeof discordUser["name"] == "undefined"||
      typeof discordUser["points"] == "undefined") {
    res.status(400).send("invalid JSON data");
  }
  await db.collection("users").doc(discordUser["name"]).set(discordUser);
  res.status(201).send(`${discordUser["name"]}'s doc successfully created`);
});

app.get("/", async (req, res) => {
  const snapshot = await db.collection("users").get();
  const users = [];
  snapshot.forEach((doc) => {
    const id = doc.id;
    const data = doc.data();
    users.push({id, ...data});
  });
  res.status(200).send(JSON.stringify(users));
});

app.get("/users/:id", async (req, res) => {
  const docRef = db.collection("users").doc(req.params.id);

  await docRef.get().then((doc) => {
    if (doc.exists) {
      const id = doc.id;
      const data = doc.data();
      const user = {id, ...data};
      console.log("user found. user data: ", data);
      res.status(200).send(JSON.stringify(user));
    } else {
      console.log("Cannot locate document!");
      res.status(404).send("user not found");
    }
  });
});

app.put("/users/:id", async (req, res) => {
  // put is used to update a user's points
  // req.body should only contain "points: <value>" where
  // <value> is the amount to increment or decrement
  const docRef = db.collection("users").doc(req.params.id);

  const value = (typeof req.body["points"] == "string") ?
  parseInt(req.body["points"], 10) :
  req.body["points"];

  if (typeof value == "undefined") {
    res.status(400).send("invalid JSON data");
  }

  await docRef.get().then((doc) => {
    if (doc.exists) {
      const id = doc.id;
      const data = doc.data();
      const incrementedValue = data["points"] + value;
      docRef.update({points: incrementedValue})
          .then(() => {
            res.status(201).send(`${id}'s points updated`);
          });
    } else {
      console.log("Cannot locate document!");
      res.status(404).send("user not found");
    }
  });
});

app.delete("/users/:id", async (req, res) => {
  await db.collection("users")
      .doc(req.params.id)
      .delete()
      .then(()=> {
        console.log("Document successfully deleted");
        res.status(200).send("Document successfully deleted!");
      }).catch((error) => {
        console.log("Error removing document: ", error);
        res.status(404).send("Document not found");
      });
});

exports.api = functions.https.onRequest(app);
