import numpy as np
import torch
from torchvision import transforms as T
from torch import Tensor
from pathlib import Path
from typing import Union, Callable

# Type for str and Path inputs
pathlike = Union[str, Path]


def convert_to_tensor(path: pathlike) -> None:
    """
    Function for converting saved ndarrays (.npy files) to torch tensors.
    Tensors will be saved in a subdirectory called 'tensor_files'.
    Array shapes: (N,H,W,3)
    Tensor shapes: (N,1,H,W)
    INPUT: path to saved ndarrays
    """
    path = Path(path)
    savedir = path/"tensor_dataset"
    savedir.mkdir(exist_ok=True)

    # convert arrays in target folder to tensor and save
    for array in path.glob("*.npy"):
        image_batch = np.load(str(array))

        # leave the first 40 frames out as they contain zoomed images
        converted = torch.from_numpy(image_batch[40:, ...])
        # transpose tensor: (n_samples, height, width, # channels) -> (# samples, # channels, h, w)
        converted = torch.einsum("nhwc -> nchw", converted)

        fp = savedir/array.stem
        torch.save(converted, fp.with_suffix(".pt"))
        

def apply(func: Callable[[Tensor], Tensor], M: Tensor, d: int = 0) -> Tensor:
    """
    Simple function to apply an operation to a tensor along the a specified dimension.
    INPUTS:
        func:   Function to be applied
        M:      Input Tensor
        d:      Dimension along which the tensor is applied
    OUTPUTS:
        res:    Processed tensor
    """
    tList = [func(m) for m in torch.unbind(M, dim=d) ]
    res = torch.stack(tList, dim=d)

    return res 


def convert_to_grayscale(path: pathlike) -> None:
    """
    Converts RGB image samples in torch tensors to grayscale.
    Tensors should have the dimensions (N, H, W, 3).
    Saved tensors will have the form (N, 1, H, W).
    INPUT: path to saved torch tensors
    """
    path = Path(path)
    savedir = path/"grayscale_dataset"
    savedir.mkdir(exist_ok=True)

    # grayscaling pipeline using torch transforms
    grayscaler = T.Compose([T.ToPILImage(),
                        T.Grayscale(num_output_channels=3),
                        T.ToTensor()])
    
    for file in path.glob("*.pt"):
        batch = torch.load(str(file))
        converted = apply(grayscaler, batch)

        fp = savedir/file.stem
        torch.save(converted, fp.with_suffix(".pt"))


def cat_tensors(path: pathlike, d: int = 0) -> None:
    """
    Script to look for saved tensors in a folder and concatenate them along a defined axis.
    INPUT:
        path:   path to check for saved fiels
        d:      concatenation dimension
    """
    path = Path(path)

    tlist = []
    for file in path.glob("*.pt"):
        batch = torch.load(str(file))
        tlist.append(batch)

    res = torch.cat(tlist, dim=d)
    fp = path/"cat_data.pt"
    torch.save(res, str(fp))


def main():
    path = "/home/timo/DataSets/carracer_images/"
    convert_to_tensor(path)
    dset_path = "/home/timo/DataSets/carracer_images/tensor_dataset"
    convert_to_grayscale(dset_path)


if __name__ == '__main__':
        main()