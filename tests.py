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
        

if __name__ == '__main__':
    unittest.main()
