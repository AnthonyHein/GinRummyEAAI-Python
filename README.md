# GinRummyEAAI-Python
Gin Rummy software for the Gin Rummy EAAI Undergraduate Research Challenge (translated to Python).

Found in Java by Todd Neller here: https://github.com/tneller/gin-rummy-eaai

PrincetonGinPlayer.class is the current submission, compiled with the provided vermouth.jar. Check [here](https://github.com/MTU-Tonic/vermouth/tree/master) for the tournament code.

Test with:

```shell
javac -cp ".:./vermouth.jar" PrincetonGinPlayer.java
javac -cp ".:./vermouth.jar" SimpleGinRummyPlayer.java
java -jar vermouth.jar    --oneall    --games 100    --agents 'file:./PrincetonGinPlayer' 'file:./SimpleGinRummyPlayer'
```

Verifying that it is working will require that you open up the .csv file in the resulting .zip directory and do some Excel equations on it.

**The Python Server.py must be running during this process.**
