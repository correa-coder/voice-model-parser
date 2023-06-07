import unittest

from utils.parsers import VoiceModelParser


class ParserTests(unittest.TestCase):
    
    def test_extract_epochs(self):
        self.assertEqual(VoiceModelParser.extract_epochs('ModelName (RVC v2) 44k steps'), -1)
        self.assertEqual(VoiceModelParser.extract_epochs('ModelName (RVC v2)'), -1)
        self.assertEqual(VoiceModelParser.extract_epochs('ModelName (RVC v2) 800 epoch'), 800)
        self.assertEqual(VoiceModelParser.extract_epochs('ModelName (RVC v2) 800 epochs'), 800)
        self.assertEqual(VoiceModelParser.extract_epochs('ModelName (RVC v2) 1k Epoch'), 1000)
        self.assertEqual(VoiceModelParser.extract_epochs('ModelName (RVC v2) 1.2k Epochs'), 1200)
        self.assertEqual(VoiceModelParser.extract_epochs('ModelName (RVC v2) 1.05k Epoch'), 1050)
        self.assertEqual(VoiceModelParser.extract_epochs('ModelName (RVC v2) 2k EPOCH'), 2000)
        self.assertEqual(VoiceModelParser.extract_epochs('ModelName (250 EPOCHS)'), 250)

    def test_extract_steps(self):
        self.assertEqual(VoiceModelParser.extract_steps('ModelName (RVC v2) 800 epochs'), -1)
        self.assertEqual(VoiceModelParser.extract_steps('ModelName (RVC v2) 100 step'), 100)
        self.assertEqual(VoiceModelParser.extract_steps('ModelName (RVC v2) 44k steps'), 44000)
        self.assertEqual(VoiceModelParser.extract_steps('ModelName (RVC v2) 44k STEP'), 44000)
        self.assertEqual(VoiceModelParser.extract_steps('ModelName (RVC v2) (44.12k STEPS)'), 44120)

    def test_extract_name(self):
        self.assertEqual(VoiceModelParser.extract_name('Jhay Cortez (RVC) 250 Epoch'), 'Jhay Cortez')
        self.assertEqual(VoiceModelParser.extract_name('Gummibär (RVC v2) 300 Epoch'), 'Gummibär')
        self.assertEqual(VoiceModelParser.extract_name('Jeno (From NCT) (RVC) 350 Epoch 11k Steps'), 'Jeno (From NCT)')
        self.assertEqual(VoiceModelParser.extract_name('Maeve (From Paladins) RVC 1.6k Epoch'), 'Maeve (From Paladins)')
        self.assertEqual(VoiceModelParser.extract_name('Britney Spears 100k', is_rvc=False), 'Britney Spears')
        self.assertEqual(VoiceModelParser.extract_name('Britney Spears', is_rvc=False), 'Britney Spears')

    def test_extract_links(self):
        sample1 = 'Here is the link https://drive.google.com/file/d/1Rn7dOfD3BvZjUP36pAEv8VCYJC9clogS/view?usp=sharing'
        sample1_links = ['https://drive.google.com/file/d/1Rn7dOfD3BvZjUP36pAEv8VCYJC9clogS/view?usp=sharing']
        self.assertEqual(VoiceModelParser.extract_links(sample1), sample1_links)

        sample2 = 'Model: https://drive.google.com/file/d/1Rn7dOfD3BvZjUP36pAEv8VCYJC9clogS/view?usp=sharing\nDataset: https://drive.google.com/file/d/1Rn7dOfD3BvZjUP36pAEv8VCYJC9clogS/view?usp=sharing'
        sample2_links = [
            'https://drive.google.com/file/d/1Rn7dOfD3BvZjUP36pAEv8VCYJC9clogS/view?usp=sharing',
            'https://drive.google.com/file/d/1Rn7dOfD3BvZjUP36pAEv8VCYJC9clogS/view?usp=sharing'
        ]
        self.assertEqual(VoiceModelParser.extract_links(sample2), sample2_links)

        sample3 = 'Link 1 (MEGA): https://mega.nz/file/1fUjzTYQ#wrCJhg-r0LpRdYQJfuqao_f7JN6phJFQjrTpNlY_aVo'
        sample3_links = [
            'https://mega.nz/file/1fUjzTYQ#wrCJhg-r0LpRdYQJfuqao_f7JN6phJFQjrTpNlY_aVo'
        ]
        self.assertEqual(VoiceModelParser.extract_links(sample3), sample3_links)

if __name__ == '__main__':
    unittest.main()
