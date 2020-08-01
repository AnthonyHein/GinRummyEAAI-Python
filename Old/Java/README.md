*For this to work you need to go to [here](https://www.tensorflow.org/install/lang_java) and download the appropriate jni.
Then place the uncompressed directory in the Java directory with the name jni.*

## Compile

$ javac -cp libtensorflow.jar LoadTensorflowModel.java

## Run

$ java -cp libtensorflow.jar:. -Djava.library.path=./jni LoadTensorflowModel

## Notes

There were previously issues finding the nodes. I have found a way to print out the
nodes (among several other things). Investigating how to cherry-pick what gets printed:

```java
// For a TensorFlow Graph g
Iterator<Operation> ops = g.operations();
while (ops.hasNext()) {
    System.out.println(ops.next().name());
}
```

This is one way of doing that:

```java
// Print for tags.
Iterator<Operation> ops = g.operations();
while (ops.hasNext()) {
    Operation op = ops.next();
    // Types are: Add, Const, Placeholder, Sigmoid, MatMul, Identity
    if (op.type().equals("Placeholder")) {
        System.out.println("Type: " + op.type() + ", Name: " + op.name());
    }
}
```
