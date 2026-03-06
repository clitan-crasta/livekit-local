// import express from "express";

// import grpc from "@grpc/grpc-js";
// import * as protoLoader from "@grpc/proto-loader";
// import path from "node:path";
// import { dirname } from 'node:path';

// const PROTO_PATH = path.join("./application.proto");

// const packageDefination = protoLoader.loadSync(PROTO_PATH);
// const proto: any = grpc.loadPackageDefinition(packageDefination).ApplicationOne;

// function sayHello(args: any, callback: any) {
//   const message = {
//     message: `Hello ${args.request.name}`,
//   };
//   callback(null, message);
// }

// function main() {
//   const server = new grpc.Server();
//   server.addService(proto.ApplicationOne.service, { SayHello: sayHello });
//   server.bindAsync(
//     "0.0.0.0:4000",
//     grpc.ServerCredentials.createInsecure(),
//     (err, port) => {
//       if (err) {
//         console.log("failed to start server");
//         return;
//       }
//       console.log("server runing on port 4000");
//     },
//   );
// }

// main();

import express from "express";
import cors from 'cors';

const app = express();

app.use(cors())
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.get("/app", (req, res, next) => {
  console.log("api called")
  res.send({
    applicationName: "Heaps",
  });
});

app.post("/save", (req, res, next) => {
  console.log(req.body);
  res.send({
    status: "Ok",
    message: "record saved successfully",
  });
});

app.listen(4000, () => {
  console.log("app runnig on port 4000");
});
