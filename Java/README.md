*For this to work you need to go to [here](https://www.tensorflow.org/install/lang_java) and download the appropriate jni.
Then place the uncompressed directory in the Java directory with the name jni.*

## Compile

$ javac -cp libtensorflow.jar LoadTensorflowModel.java

## Run

$ java -cp libtensorflow.jar:. -Djava.library.path=./jni LoadTensorflowModel
