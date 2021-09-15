import pygame


class SpriteSheet:
    def __init__(self, filename):
        try:
            self.sheet = pygame.image.load(filename).convert()
        except pygame.error as message:
            print('Unable to load spritesheet image:', filename)
            raise SystemExit(message)

    # Load a specific image from a specific rectangle
    def image_at(self, rectangle, color_key=None):
        """Loads image from x,y,x+offset,y+offset"""
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if color_key is not None:
            if color_key == -1:
                color_key = image.get_at((0, 0))
            image.set_colorkey(color_key, pygame.RLEACCEL)
        return image

    # Load a whole bunch of images and return them as a list
    def images_at(self, rects, color_key=None):
        """Loads multiple images, supply a list of coordinates"""
        return [self.image_at(rect, color_key) for rect in rects]

    # Load a whole strip of images
    def load_strip(self, rect, image_count, color_key=None):
        """Loads a strip of images and returns them as a list"""
        tups = [(rect[0] + rect[2] * x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, color_key)


def test_floor(coords):
    if coords['x'] < 120 and coords['y'] == 240 - 16 - 8:
        return True
    elif coords['x'] >= 120 and coords['y'] == 240 - 16 - 8 - 1 - ((coords['x'] - 120) // 16):
        return True
    else:
        for level in range(1, 3):
            if coords['x'] <= 256-25-15 and coords['y'] == 201 - 16 - 64 * (level - 1) - ((240 - coords['x'] + 7) // 16):
                return True
            if coords['x'] >= 24 and coords['y'] == 167 - 16 - 64 * (level - 1) - ((coords['x'] - 8) // 16):
                return True

    return False
