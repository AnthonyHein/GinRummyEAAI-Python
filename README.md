# GinRummyEAAI-Python
Gin Rummy software for the Gin Rummy EAAI Undergraduate Research Challenge (translated to Python).

Found in Java by Todd Neller here: https://github.com/tneller/gin-rummy-eaai

PrincetonGinPlayer.class is the current submission, compiled with the provided vermouth.jar.

Test with:

```shell
javac -cp ".:./vermouth.jar" PrincetonGinPlayer.java
java -jar vermouth.jar    --oneall    --games 100    --agents 'file:./PrincetonGinPlayer' 'file:./PrincetonGinPlayer'
```

Alternatively, move a copy of SimpleGinRummyPlayer.java to the outer folder, change line 1 to:

```java
import ginrummy.*;
```

Change line 36 to:

```java
public class SimpleGinRummyPlayer implements ginrummy.GinRummyPlayer {
    ...
}
```

Finally, run:

```shell
javac -cp ".:./vermouth.jar" PrincetonGinPlayer.java
javac -cp ".:./vermouth.jar" SimpleGinRummyPlayer.java
java -jar vermouth.jar    --oneall    --games 100    --agents 'file:./PrincetonGinPlayer' 'file:./SimpleGinRummyPlayer'
```

Verifying that it is working will require that you open up the .csv file in the resulting .zip directory and do some Excel equations on it.

**The Python Server.py must be running during this process.**
