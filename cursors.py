
import pygame
# pygame must be inited already



def compile( hotspot, array ):

    size = len( array[0] ), len( array )

    return (size,hotspot) + pygame.cursors.compile( array, black='.', white='X' )



finger = compile( (5,1), (
'     XX         ',
'    X..X        ',
'    X..X        ',
'    X..X        ',
'    X..XXX      ',
'    X..X..XX    ',
'    X..X..X.X   ',
'    X..X..X..X  ',
'XXX X..X..X..X  ',
'X..XX........X  ',
'X...X........X  ',
' X...........X  ',
'  X..........X  ',
'  X..........X  ',
'   X........X   ',
'    X.......X   ',
'    X......X    ',
'     X.....X    ',
'     XXXXXXX    ',
'                ',
'                ',
'                ',
'                ',
'                ') )


arrow = compile( (0,0), (
'X               ',
'XX              ',
'X.X             ',
'X..X            ',
'X...X           ',
'X....X          ',
'X.....X         ',
'X......X        ',
'X.......X       ',
'X........X      ',
'X.........X     ',
'X......XXXXX    ',
'X...X..X        ',
'X..XX..X        ',
'X.X  X..X       ',
'XX   X..X       ',
'X     X..X      ',
'      X..X      ',
'       X..X     ',
'       X..X     ',
'        XX      ',
'                ',
'                ',
'                ',) )

                