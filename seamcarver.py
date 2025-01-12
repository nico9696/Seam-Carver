# to run whole program, run in cmd terminal (inside "seamcarving_files" folder): seamcarvingenv\Scripts\activate 
# to run this file: python seamcarver.py 

#!/usr/bin/env python3

from picture import Picture

class SeamCarver(Picture):
    def energy(self, i: int, j: int) -> float:
        '''
        Return the energy of pixel at column i and row j
        '''

        # EXCEPTION 1
        # (CHATGPT for syntax) Check if indices are within bounds
        if not (0 <= i <= self._width - 1):
            raise IndexError(f"Index i={i} out of bounds for width={self._width}.")
        if not (0 <= j <= self._height - 1):
            raise IndexError(f"Index j={j} out of bounds for height={self._height}.")

        # WIDTH
        # if pixel is at leftmost, it goes to the rightmost
        # if pixel is at an appropriate spot, it stays as is
        # if pixel on rightmost, it will automatically go to 0
        Rx = self[(i - 1) % self._width, j][0] - self[(i + 1) % self._width, j][0]
        Gx = self[(i - 1) % self._width, j][1] - self[(i + 1) % self._width, j][1]
        Bx = self[(i - 1) % self._width, j][2] - self[(i + 1) % self._width, j][2]

        # HEIGHT
        Ry = self[i, (j - 1) % self._height][0] - self[i, (j + 1) % self._height][0]
        Gy = self[i, (j - 1) % self._height][1] - self[i, (j + 1) % self._height][1]
        By = self[i, (j - 1) % self._height][2] - self[i, (j + 1) % self._height][2]

        x = Rx**2 + Gx**2 + Bx**2
        y = Ry**2 + Gy**2 + By**2
        energy = (x + y)**0.5

        return energy




    def find_vertical_seam(self) -> list[int]: 
        '''
        my idea:
        Since this must run in at most O(WH) time, 
        O(W) would be traversing each row.
        This will be done H number of time (O(H)).
        A matrix will be made (each row being the accumulated energy of that pixel).
        Once the bottom is reached, the minimum pixel is taken.
        Backtrack by going to that pixel, then seeing which among its top-left, top, and top-right is the least.
        This will create the index list.

        i got this
        '''

        '''
        Return a sequence of indices representing the lowest-energy
        vertical seam
        '''

        # EXCEPTION 3 (if this method is called when picture is of width 1)
        if self._width == 1:
            raise SeamError(f"Picture is of width 1")

        accumulated_energy_matrix = [] # matrix where each row is the accumulated enrtgy of the pixels on that level   

        for i in range(self._height): # this repeats for each row

            cur = []

            if i == 0: # only for 1st row
                for j in range(self._width): # makes list of energies of 1st row
                    cur.append(self.energy(j, i))  # Pass column (j) and row (i) directly to the energy method  
                accumulated_energy_matrix.append(cur)
                continue

            else:
                for j in range(self._width): # this repeats for every pixel in a row (except the 1st row)
                    
                    if j > 0: 
                        top_left = accumulated_energy_matrix[i - 1][j - 1] 
                    else: # j is at the left-most pixel
                        top_left = 1e20 # infinitely large number

                    top = accumulated_energy_matrix[i - 1][j]
                    
                    if j < self._width - 1:
                        top_right = accumulated_energy_matrix[i - 1][j + 1] 
                    else: # j is at the right-most pixel
                        top_right = 1e20 # infinitely large number

                    min_energy = self.energy(j, i) + min(top_left, top, top_right)
                    # (^explanation^) min_energy = (energy of that individual pixel) + (accumulated energy from the 1 of the 3 choices from the previous row of pixels) 
                    cur.append(min_energy)  
                accumulated_energy_matrix.append(cur) 

        # ------------------------------------------------------------------------------------------------------------------------------------------

        sorted_last_row = sorted(accumulated_energy_matrix[-1]) # sorting accumulated energies of last row (so that in case seam spans from corner to corner, we have backups)
        
        while True: # if seam spans corner to corner, this runs again
            min_last_pixel = min(sorted_last_row) # minimum of the sorted last row (will be used to find seam)
            # ^if first min_last_pixel spans corner to corner, it is deleted so the next minimum can be used

            seam = [] # list of indexes to be returned
            seam.append(accumulated_energy_matrix[-1].index(min_last_pixel)) # appends index of min_last_pixel
            count = len(accumulated_energy_matrix) - 2 # starts at 2nd to the last row
            while count >= 0: # from 2nd to the last row to 1st row

                seam_index = seam[0]  # Get the current seam's column index

                if seam_index > 0: 
                    top_left = accumulated_energy_matrix[count][seam_index - 1]
                else: # if seam_index (the seam in question) is at the left-most pixel
                    top_left = 1e20 # infinitely large number

                top = accumulated_energy_matrix[count][seam_index]
                
                if seam_index < self._width - 1:
                    top_right = accumulated_energy_matrix[count][seam_index + 1] 
                else: # if seam_index (the seam in question) is at the right-most pixel
                    top_right = 1e20 # infinitely large number

                min_value = min(top_left, top, top_right) # of the values of the 3 indexes, this determines the least

                # this if-else thing gets the index of whatever min_value is
                if min_value == top_left:
                    index = seam_index - 1
                elif min_value == top:
                    index = seam_index 
                elif min_value == top_right:
                    index = seam_index + 1

                seam.insert(0, index) # inserted to the front of seam
                count -= 1

            if abs(seam[0] - seam[-1]) + 1 == self._width: # if seam spans corner to corner delete the minimum pixel fromt he last row is deleted. In its place is the 2nd min pixel as the loop runs all over again
                del sorted_last_row[0]
            else: # if seam does not span corner to corner, the loop breaks and the seam is returned
                break

        return seam


    def find_horizontal_seam(self) -> list[int]: 
        '''
        Return a sequence of indices representing the lowest-energy
        horizontal seam
        '''

        # EXCEPTION 3 (if this method is called when picture is of height 1)
        if self._height == 1:
            raise SeamError(f"Picture is of height 1")

        # this makes a matrix for the energies of each pixel (NOT ACCUMULATED)... only for finding horizontal seam because need to transpose image
        energy_matrix = []
        for i in range(self._height): # this repeats for each row
            cur = []
            for j in range(self._width): # makes list of energies of each row
                cur.append(self.energy(j, i))   
            energy_matrix.append(cur)


        transposed = list(map(list, zip(*energy_matrix))) # (CHATGPT) - transposes energy_matrix so that it does things just like when finding vertical seam
        transposed_height = len(transposed)
        transposed_width = len(transposed[0])

        accumulated_energy_matrix = [] # matrix where each row is the accumulated energy of the pixels on that level   

        for i in range(transposed_height): # this repeats for each row

            cur = []

            if i == 0: # only for 1st row
                for j in range(transposed_width): # makes list of energies of 1st row
                    cur.append(transposed[i][j])   
                accumulated_energy_matrix.append(cur)
                continue

            else:
                for j in range(transposed_width): # this repeats for every pixel in a row (except the 1st row)

                    if j > 0: 
                        top_left = accumulated_energy_matrix[i - 1][j - 1] 
                    else: # j is at the left-most pixel
                        top_left = 1e20 # infinitely large number

                    top = accumulated_energy_matrix[i - 1][j]

                    if j < transposed_width - 1:
                        top_right = accumulated_energy_matrix[i - 1][j + 1] 
                    else: # j is at the right-most pixel
                        top_right = 1e20 # infinitely large number

                    min_energy = transposed[i][j] + min(top_left, top, top_right)
                    # (^explaation^) min_energy = (energy of that individual pixel) + (accumulated energy from the 1 of the 3 choices from the previous row of pixels) 
                    cur.append(min_energy)  
                accumulated_energy_matrix.append(cur) 

        # -------------------------------------------------------------------------------------------------------------------------------------------

        sorted_last_row = sorted(accumulated_energy_matrix[-1]) # sorting accumulated energies of last row (so that in case seam spans from corner to corner, we have backups)

        while True: # if seam spans corner to corner, this runs again
            min_last_pixel = min(sorted_last_row) # minimum of the sorted last row (will be used to find seam)
            # ^if first min_last_pixel spans corner to corner, it is deleted so the next minimum can be used

            seam = [] # list of indexes to be returned
            seam.append(accumulated_energy_matrix[-1].index(min_last_pixel)) # appends index of min_last_pixel
            count = len(accumulated_energy_matrix) - 2 # starts at 2nd to the last row
            while count >= 0: # from 2nd to the last row to 1st row

                seam_index = seam[0]  # Get the current seam's column index

                if seam_index > 0: 
                    top_left = accumulated_energy_matrix[count][seam_index - 1]
                else: # if seam_index (the seam in question) is at the left-most pixel
                    top_left = 1e20 # infinitely large number

                top = accumulated_energy_matrix[count][seam_index]
                
                if seam_index < transposed_width - 1:
                    top_right = accumulated_energy_matrix[count][seam_index + 1] 
                else: # if seam_index (the seam in question) is at the right-most pixel
                    top_right = 1e20 # infinitely large number

                min_value = min(top_left, top, top_right) # of the values of the 3 indexes, this determines the least

                # this if-else thing gets the index of whatever min_value is
                if min_value == top_left:
                    index = seam_index - 1
                elif min_value == top:
                    index = seam_index 
                elif min_value == top_right:
                    index = seam_index + 1

                seam.insert(0, index) # inserted to the front of seam
                count -= 1

            if abs(seam[0] - seam[-1]) + 1 == transposed_width: # if seam spans corner to corner delete the minimum pixel fromt he last row is deleted. In its place is the 2nd min pixel as the loop runs all over again
                del sorted_last_row[0]
            else: # if seam does not span corner to corner, the loop breaks and the seam is returned
                break


        return(seam)

        
        

    def remove_vertical_seam(self, seam: list[int]):
        '''
        Remove a vertical seam from the picture
        '''

        # EXCEPTION 3 (if this method is called when picture is of width 1)
        if self._width == 1:
            raise SeamError(f"Picture is of width 1")

        # EXCEPTION 2 (if seam height is wrong)
        if len(seam) != self._height:
            raise SeamError(f"Wrong seam height.")
        
        for i in range(len(seam)): # iterating given vertical seam

            # EXCEPTION 2 (if indexes of seam differs by more than 1)
            if i + 1 < self._height and abs(seam[i] - seam[i + 1]) > 1:
                raise SeamError(f"Two consecutive indexes in seam differs by more than 1")

            for j in range(seam[i], self._width - 1): # iterating from the given pixel in the row UNTIL the end of the row
                self[j, i] = self[j + 1, i] # copying the pixel on the right into the current pixel
            del self[self._width - 1, i] # deleting the last pixel of the row after moving all the pixels to the left
        self._width -= 1 # decrementing width of picture


    def remove_horizontal_seam(self, seam: list[int]):
        '''
        Remove a horizontal seam from the picture
        '''

        # EXCEPTION 3 (if this method is called when picture is of height 1)
        if self._height == 1:
            raise SeamError(f"Picture is of height 1")

        # EXCEPTION 2 (if seam width is wrong)
        if len(seam) != self._width:
            raise SeamError(f"Wrong seam width.")

        for i in range(len(seam)): # iterating given horizontal seam

            # EXCEPTION 2 (if indexes of seam differs by more than 1)
            if i + 1 < self._width and abs(seam[i] - seam[i + 1]) > 1:
                raise SeamError(f"Two consecutive indexes in seam differs by more than 1")

            for j in range(seam[i], self._height - 1): # iterating from the given pixel in the column UNTIL the end of the column
                self[i, j] = self[i, j + 1] # copying the pixel on the bottom into the current pixel
            del self[i, self._height - 1] # deleting the last pixel of the column after moving all the pixels to the top
        self._height -= 1 # decrementing height of picture



class SeamError(Exception):
    pass