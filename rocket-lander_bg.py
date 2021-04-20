provide {
    make-lander: make-lander,
    demo-lander: demo-lander,
    delta-t: delta-t,
    WIDTH: WIDTH,
    HEIGHT: HEIGHT,
    ground-height: ground-height,
    default-next-x: default-next-x,
    default-is-onscreen-x: default-is-onscreen-x,
    default-next-y: default-next-y,
    default-next-vy: default-next-vy,
    default-force-for-key: default-force-for-key,
    default-sum-of-forces: default-sum-of-forces,
    default-a-from-f: default-a-from-f,
    default-game-status: default-game-status
} end

include image
include reactors

var provided-gfs = -3.711

WIDTH = 800
HEIGHT = 600
GROUND-MAX = 150
SPACE = rectangle(WIDTH, HEIGHT, "solid", "black")
fun make-planet(img):
  img-width = image-width(img)
  img-height = image-height(img)
  scaled-img = 
    if (img-width >= WIDTH) and (img-height >= GROUND-MAX): img
    else: scale(num-max(GROUND-MAX / img-height, WIDTH / img-width), frame(img))
    end
  crop-x = num-max((image-width(scaled-img) - WIDTH) / 2, 0)
  crop(crop-x, 0, WIDTH, GROUND-MAX, scaled-img)
end
heights = [list:
  {0; 60},
  {120; 60}, # At x = 0, y = 60; rising smoothly to y = 60 at x = 120
  {140; 70},
  {180; 70},
  {270; 100},
  {400; 115},
  {500; 100},
  {645; 100},
  {800; 110}
]
fun ground-help(x, prev, rest):
  cases(List) rest:
    | empty => prev.{1}
    | link(next, tail) =>
      if (x <= next.{0}): 
        alpha = ((x - prev.{0}) / (next.{0} - prev.{0}))
        prev.{1} + ((next.{1} - prev.{1}) * alpha)
      else: ground-help(x, next, tail)
      end
  end
end
  
fun ground-height(x):
  ground-help(x, heights.first, heights.rest)
end



fun make-lander(planet-img, rocket-img, m, vx, gy, 
    next-x, is-onscreen-x,
    next-y, next-vy, 
    a-from-f,
    force-for-key, sum-forces, game-status) block:
  provided-gfs := gy
  PLANET = make-planet(planet-img)
  BACKGROUND = overlay-align("middle", "bottom", PLANET, SPACE)
  raw-flames = 
    image-url("https://code.pyret.org/shared-image-contents?" + 
      "sharedImageId=1AHFPbu54o2joGarFF_yvzHBtfPHtYlk0")
  FLAMES = scale(0.5 * (image-width(rocket-img) / image-width(raw-flames)),
    raw-flames)
  rocket-half-height = image-height(rocket-img) / 2
  flames-half-height = image-height(FLAMES) / 2
  game = reactor:
    init: {
        image-width(rocket-img) / 2; HEIGHT - (5 * rocket-half-height); 
        vx; 0; 
        0 - num-abs(gy * m); 0 # NOTE: Ensuring the sign convention for now; should fix later
      },
    title: "Lander!",
    on-tick: lam(s):
        new-x = if is-onscreen-x(s.{0}): next-x(s.{0}, s.{2}) else: 0 end
        new-ay = a-from-f(sum-forces(s.{4}, s.{5}))
        new-vy = next-vy(s.{3}, new-ay)
        new-y = next-y(s.{1}, new-vy)
        {new-x; new-y; vx; new-vy; s.{4}; s.{5}}
      end,
    on-key: lam(s, key):
        {s.{0}; s.{1}; s.{2}; s.{3}; s.{4}; force-for-key(s.{5}, key)}
      end,
    to-draw: lam(s):
        rocket-bkg = 
          put-image(rocket-img, s.{0}, s.{1} + rocket-half-height, BACKGROUND)
        with-flames =
          ask:
            | s.{5} < 0 then:
              put-image(rotate(180, FLAMES),
                s.{0}, s.{1} + flames-half-height + (2 * rocket-half-height),
                rocket-bkg)
            | s.{5} > 0 then:
              put-image(FLAMES,
                s.{0}, s.{1} - flames-half-height,
                rocket-bkg)
            | otherwise: rocket-bkg
          end
        overlay-align("middle", "top", 
          above(
            text(game-status(s.{0}, s.{1}, s.{2}, s.{3}), 30, "white"),
            text("x = " + num-to-string-digits(s.{0}, 3) +
              ", y = " + num-to-string-digits(s.{1}, 3) +
              ", vy = " + num-to-string-digits(s.{3}, 3) +
              ", thrust-y = " + num-to-string-digits(s.{5}, 3), 20, "light gray")),
              with-flames)
      end,
    stop-when: lam(s):
        s.{1} < ground-height(s.{0})
      end
  end
  interact(game)
  nothing
end

delta-t = 0.05

###########################################################################
# INERT CODE BELOW
MARS = image-url("https://code.pyret.org/shared-image-contents?" + 
  "sharedImageId=1fCcB6IuEUJN3JNsksDE0gtCAXc7-Qw_5")
ROCKET = scale(0.2, image-url("https://code.pyret.org/shared-image-contents?sharedImageId=1npNv8bo_6cSn-s0x_I3PtMAVoXtsUDtJ"))
mass = 533 # kg
v-x = 35 # m/s
gfs = -3.711 # N/kg

# Computes the next x-position of the rocket, given its 
# current position and velocity
fun default-next-x(x, vx):
  x
end

fun default-is-onscreen-x(x):
  true
end

# Computes the next y-position of the rocket, given its 
# current position and velocity
fun default-next-y(y, vy):
  y
end

# Computes the next y-velocity of the rocket, given its 
# current velocity and acceleration
fun default-next-vy(vy, ay):
  vy
end

# Computes the net force on the rocket, to determine acceleration
# NOTE: Could be `net-accel` instead of `net-force`, but that's up 
# to physics folks
fun default-sum-of-forces(g-force, rocket-force):
  g-force
end

fun default-a-from-f(net-force):
  provided-gfs
end

# Captions the game with a status message
fun default-game-status(x, y, vx, vy):
  "Flying"
end

# Controls the throttle, to determine the force applied to the rocket.
# NOTE: Can totally cheat here and be non-physical, by returning a negative 
# force...
fun default-force-for-key(cur-force, key):
  cur-force
end

fun demo-lander():
  make-lander(
    MARS, ROCKET, # IMAGES
    mass, v-x, gfs, # PARAMETERS
    default-next-x, default-is-onscreen-x,
    default-next-y, default-next-vy,
    default-a-from-f,
    default-force-for-key, default-sum-of-forces, default-game-status # controllers
    )
end
