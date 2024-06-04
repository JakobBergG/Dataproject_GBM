# DOES NOT WORK
import torch
import torch.nn as nn
from torchviz import make_dot

# Define custom layers used in the network
class ConvDropoutNormNonlin(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size, stride, padding):
        super(ConvDropoutNormNonlin, self).__init__()
        self.conv = nn.Conv3d(in_channels, out_channels, kernel_size, stride, padding)
        self.instnorm = nn.InstanceNorm3d(out_channels, eps=1e-05, momentum=0.1, affine=True, track_running_stats=False)
        self.lrelu = nn.LeakyReLU(negative_slope=0.01, inplace=True)

    def forward(self, x):
        x = self.conv(x)
        x = self.instnorm(x)
        x = self.lrelu(x)
        return x

class StackedConvLayers(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(StackedConvLayers, self).__init__()
        self.blocks = nn.Sequential(
            ConvDropoutNormNonlin(in_channels, out_channels, kernel_size=3, stride=1, padding=1)
        )

    def forward(self, x):
        return self.blocks(x)

# Define the main Generic_UNet model
class Generic_UNet(nn.Module):
    def __init__(self):
        super(Generic_UNet, self).__init__()

        self.conv_blocks_localization = nn.ModuleList([
            nn.Sequential(
                StackedConvLayers(640, 320),
                StackedConvLayers(320, 320)
            ),
            nn.Sequential(
                StackedConvLayers(512, 256),
                StackedConvLayers(256, 256)
            ),
            nn.Sequential(
                StackedConvLayers(256, 128),
                StackedConvLayers(128, 128)
            ),
            nn.Sequential(
                StackedConvLayers(128, 64),
                StackedConvLayers(64, 64)
            ),
            nn.Sequential(
                StackedConvLayers(64, 32),
                StackedConvLayers(32, 32)
            )
        ])

        self.conv_blocks_context = nn.ModuleList([
            nn.Sequential(
                ConvDropoutNormNonlin(1, 32, kernel_size=3, stride=1, padding=1),
                ConvDropoutNormNonlin(32, 32, kernel_size=3, stride=1, padding=1)
            ),
            nn.Sequential(
                ConvDropoutNormNonlin(32, 64, kernel_size=3, stride=2, padding=1),
                ConvDropoutNormNonlin(64, 64, kernel_size=3, stride=1, padding=1)
            ),
            nn.Sequential(
                ConvDropoutNormNonlin(64, 128, kernel_size=3, stride=2, padding=1),
                ConvDropoutNormNonlin(128, 128, kernel_size=3, stride=1, padding=1)
            ),
            nn.Sequential(
                ConvDropoutNormNonlin(128, 256, kernel_size=3, stride=2, padding=1),
                ConvDropoutNormNonlin(256, 256, kernel_size=3, stride=1, padding=1)
            ),
            nn.Sequential(
                ConvDropoutNormNonlin(256, 320, kernel_size=3, stride=2, padding=1),
                ConvDropoutNormNonlin(320, 320, kernel_size=3, stride=1, padding=1)
            ),
            nn.Sequential(
                ConvDropoutNormNonlin(320, 320, kernel_size=3, stride=1, padding=1),
                ConvDropoutNormNonlin(320, 320, kernel_size=3, stride=1, padding=1)
            )
        ])

        self.tu = nn.ModuleList([
            nn.ConvTranspose3d(320, 320, kernel_size=(1, 2, 2), stride=(1, 2, 2), bias=False),
            nn.ConvTranspose3d(320, 256, kernel_size=(2, 2, 2), stride=(2, 2, 2), bias=False),
            nn.ConvTranspose3d(256, 128, kernel_size=(2, 2, 2), stride=(2, 2, 2), bias=False),
            nn.ConvTranspose3d(128, 64, kernel_size=(2, 2, 2), stride=(2, 2, 2), bias=False),
            nn.ConvTranspose3d(64, 32, kernel_size=(2, 2, 2), stride=(2, 2, 2), bias=False)
        ])

        self.seg_outputs = nn.ModuleList([
            nn.Conv3d(320, 2, kernel_size=(1, 1, 1), stride=(1, 1, 1), bias=False),
            nn.Conv3d(256, 2, kernel_size=(1, 1, 1), stride=(1, 1, 1), bias=False),
            nn.Conv3d(128, 2, kernel_size=(1, 1, 1), stride=(1, 1, 1), bias=False),
            nn.Conv3d(64, 2, kernel_size=(1, 1, 1), stride=(1, 1, 1), bias=False),
            nn.Conv3d(32, 2, kernel_size=(1, 1, 1), stride=(1, 1, 1), bias=False)
        ])

    def forward(self, x):
        # Just a dummy forward to allow tracing
        for layer in self.conv_blocks_context:
            x = layer(x)
        return x

# Create an instance of the model
model = Generic_UNet()

# Create a dummy input tensor
dummy_input = torch.zeros([1, 1, 64, 64, 64])

# Generate the graph using torchviz
out = model(dummy_input)
dot = make_dot(out, params=dict(model.named_parameters()))

# Save the graph as a PNG file
dot.format = 'png'
dot.render('ANOUK_architecture')

# Display the graph
dot.view()
