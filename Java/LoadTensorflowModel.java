import org.tensorflow.*;
import java.util.*;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;


// TRY WITH OUR MODEL
public class LoadTensorflowModel {

    public static void main(String[] args) throws Exception {
        //Get absolute path to src/main/resources/saved_model.pb
        Path modelPath = Paths.get("saved_graph_file");
        byte[] graph = Files.readAllBytes(modelPath);

        // SavedModelBundle svd = SavedModelBundle.load("gin_rummy_nfsp4", "serve");
        // System.out.println(svd.metaGraphDef());

        try (Graph g = new Graph()) {

            g.importGraphDef(graph);

            // Print for tags.
            Iterator<Operation> ops = g.operations();
            while (ops.hasNext()) {
                Operation op = ops.next();
                // Types are: Add, Const, Placeholder, Sigmoid, MatMul, Identity
                if (op.type().equals("Placeholder")) {
                    System.out.println("Type: " + op.type() + ", Name: " + op.name());
                }
            }

            //open session using imported graph
            try (Session sess = new Session(g)) {
                float[][] inputData = {{4, 3, 2, 1}};

                // We have to create tensor to feed it to session,
                // unlike in Python where you just pass Numpy array
                Tensor inputTensor = Tensor.create(inputData, Float.class);
                float[][] output = predict(sess, inputTensor);
                for (int i = 0; i < output[0].length; i++) {
                    System.out.println(output[0][i]);
                }
            }
        }
    }

    private static float[][] predict(Session sess, Tensor inputTensor) {
        Tensor result = sess.runner()
                .feed("input", inputTensor)
                .fetch("not_activated_output").run().get(0);
        float[][] outputBuffer = new float[1][3];
        result.copyTo(outputBuffer);
        return outputBuffer;
    }

}

// EXAMPLE
// public class LoadTensorflowModel {
//
//     public static void main(String[] args) throws Exception {
//         //Get absolute path to src/main/resources/saved_model.pb
//         Path modelPath = Paths.get(LoadTensorflowModel.class.getResource("saved_model.pb").toURI());
//         byte[] graph = Files.readAllBytes(modelPath);
//
//         try (Graph g = new Graph()) {
//             g.importGraphDef(graph);
//
//             // Print for tags.
//             Iterator<Operation> ops = g.operations();
//             while (ops.hasNext()) {
//                 Operation op = ops.next();
//                 if (op.name().equals("input") || op.name().equals("not_activated_output") || op.name().equals("output")) {
//                     System.out.println("Type: " + op.type() + ", Name: " + op.name());
//                 }
//             }
//
//             //Just print needed operations for debug
//             System.out.println(g.operation("input").output(0));
//             System.out.println(g.operation("not_activated_output").output(0));
//
//             //open session using imported graph
//             try (Session sess = new Session(g)) {
//                 float[][] inputData = {{4, 3, 2, 1}};
//
//                 // We have to create tensor to feed it to session,
//                 // unlike in Python where you just pass Numpy array
//                 Tensor inputTensor = Tensor.create(inputData, Float.class);
//                 float[][] output = predict(sess, inputTensor);
//                 for (int i = 0; i < output[0].length; i++) {
//                     System.out.println(output[0][i]);
//                 }
//             }
//         }
//     }
//
//     private static float[][] predict(Session sess, Tensor inputTensor) {
//         Tensor result = sess.runner()
//                 .feed("input", inputTensor)
//                 .fetch("not_activated_output").run().get(0);
//         float[][] outputBuffer = new float[1][3];
//         result.copyTo(outputBuffer);
//         return outputBuffer;
//     }
//
// }
