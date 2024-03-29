""" Create a 3D mass histogram of the parent simulation.

Example usage:

    mpirun -np 4 grid_parent.py --input /IN/PATH/snapshot.hdf5 --output /GRID/PATH/grid.hdf5
"""
import argparse
from mpi4py import MPI
from gridder import GridGenerator


def main():
    # Initializations and preliminaries
    comm = MPI.COMM_WORLD  # get MPI communicator object
    rank = comm.rank  # rank of this process

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Get a 3D mass histogram of a SWIFT simulation."
    )
    parser.add_argument(
        "--input",
        type=str,
        help="The SWIFT snapshot to grid",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="The file path for the grid file",
    )
    parser.add_argument(
        "--cell_width",
        type=float,
        help="The width of a grid cell in Mpc",
        default=2,
    )
    parser.add_argument(
        "--pad_cells",
        type=int,
        help="The number of padding cells used either side of the slice",
        default=5,
    )
    parser.add_argument(
        "--delete_distributed",
        type=int,
        help="Should the distributed files be deleted after combination?",
        default=0,
    )
    args = parser.parse_args()

    # Create the grid instance
    gridder = GridGenerator(
        args.input, args.output, args.cell_width, pad_region=args.pad_cells
    )

    # Decompose the simulation cells into slices
    gridder.domain_decomp()
    if rank == 0:
        print("Decomposed the grid")

    # Perform the gridding
    if rank == 0:
        print("Gridding the simulation...")
    gridder.get_grid()

    comm.Barrier()
    if rank == 0:
        print("Combinging grid files...")
        gridder.combine_distributed_files(
            delete_distributed=args.delete_distributed,
        )


if __name__ == "__main__":
    main()
