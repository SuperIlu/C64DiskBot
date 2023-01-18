import droid64.d64.CbmException;
import droid64.d64.DiskImage;

color[] colorMap = new color[256];

color BG = #202020;
color FG = #FFFFFF;

String input=null;
String output=null;
String txt=null;

void settings() {
    // get parameters for rendering
    if (args != null) {
      input=args[0];
      output=args[1];
      txt=args[2];
    }
}

void setup() {
  //fullScreen();
  size(2000, 2000);

  int picSize = min(width, height);

  // clear screen
  background(BG);
  smooth();

  PFont font = loadFont("CBM-8.vlw");
  textFont(font);
  textAlign(LEFT, CENTER);
  rectMode(CORNER);

  // create rainbow colors
  colorMode(HSB, 256);
  colorMap[0] = BG;
  for (int i=1; i < 256; i++) {
    colorMap[i] = color((i+45)%256, 256, 256);

    fill(colorMap[i]);
    stroke(colorMap[i]);
    if (i%16 == 0) {
      text(str(i), 0, i*2);
    }
    line(30, i*2, 32, i*2);
    line(30, i*2+1, 32, i*2+1);
  }

  try {
    DiskImage di = DiskImage.getDiskImage(input);

    ellipseMode(RADIUS);
    int trackWidth = ((picSize/2) - (picSize/10)) / (di.getTrackCount()+1);
    println("trackWidth = "+trackWidth);
    for (int t = 1; t <= di.getTrackCount(); t++) {
      int size = picSize/2 - t*trackWidth;
      for (int s = 0; s < di.getMaxSectors(t); s++) {
        byte[] data = di.getBlock(t, s);
        println("track="+t+", sector="+s+", size="+data.length);
        double sectorSize = TWO_PI / (data.length+1) / di.getMaxSectors(t);

        int pos = s*257;
        float arcStart = (float) (sectorSize*pos);
        float arcStop = (float) (sectorSize*(pos+1));

        fill(FG);
        stroke(FG);
        arc(picSize/2, picSize/2, size, size, arcStart, arcStop);
        for (int b = 0; b < data.length; b++) {
          pos = s*257 + b + 1;
          arcStart = (float) (sectorSize*pos);
          arcStop = (float) (sectorSize*(pos+1));

          fill(colorMap[data[b] & 0xFF]);
          stroke(colorMap[data[b] & 0xFF]);
          arc(picSize/2, picSize/2, size, size, arcStart, arcStop);
        }
      }

      stroke(FG);
      noFill();
      ellipse(picSize/2, picSize/2, size, size);

      size = picSize/2 - (t+1)*trackWidth;
      stroke(FG);
      fill(BG);
      ellipse(picSize/2, picSize/2, size, size);
    }
  } 
  catch (Exception e) {
    print(e.getMessage());
    throw new RuntimeException(e);
  }

  fill(FG);
  stroke(FG);
  textAlign(CENTER, CENTER);
  text(txt.toUpperCase(), picSize/2, picSize/2);

  noLoop();
  save(output);
  exit();
}

void draw() {
}
