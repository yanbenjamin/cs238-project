	def displayGameBoard(self):
		self.setBoardColors(self.grid)

		fig, ax = plt.subplots()
		fig.suptitle(f"Target: {self.secretKana} ({self.secretWord})", 
			fontname = "Apple SD Gothic Neo", fontsize = 18, y = 0.96)
		im = ax.imshow(grid)
		for i in range(NUM_GUESSES):
			if (i >= len(self.guesses)): continue
			guess = self.guesses[i]
			for j in range(NUM_LETTERS):
				if (j >= len(guess)): continue 
				letter = guess[j]
				text = ax.text(j, i, letter, ha="center", va="center", color="black", 
					fontname = "Apple SD Gothic Neo", fontsize = 24)

		#ax.spines[:].set_visible(False)
		self.addGridLines(ax)
		plt.axis("off")
		##ax.set_xticks(np.arange(gridColors.shape[1]+1)-0.5, minor=True)
		#ax.set_yticks(np.arange(gridColors.shape[0]+1)-0.5, minor=True)
		#ax.set_xticks([])
		#ax.set_yticks([])
		plt.show()
